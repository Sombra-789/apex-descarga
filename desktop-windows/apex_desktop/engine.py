"""Integración local con yt-dlp/FFmpeg; no usa navegador ni servidor Apex."""
from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path
from threading import Event
from typing import Callable

from .models import DownloadJob, validate_url


class JobCancelled(Exception):
    """La persona usuaria canceló la tarea."""


class EngineUnavailable(RuntimeError):
    pass


def get_ytdlp():
    try:
        import yt_dlp
    except ImportError as exc:
        raise EngineUnavailable("Falta yt-dlp. Instala las dependencias con INSTALAR_Y_EJECUTAR.cmd.") from exc
    return yt_dlp


def version() -> str:
    try:
        from yt_dlp.version import __version__
        return __version__
    except ImportError:
        return "No instalado"


def ffmpeg_path() -> str | None:
    """Detecta FFmpeg instalado o situado en bin/ junto al ejecutable."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "bin" / "ffmpeg.exe")
    else:
        candidates.append(Path(__file__).resolve().parent.parent / "bin" / "ffmpeg.exe")
    for item in candidates:
        if item.is_file():
            return str(item.parent)
    result = shutil.which("ffmpeg")
    return str(Path(result).parent) if result else None


def format_expression(kind: str, quality: str, has_ffmpeg: bool) -> str:
    if kind == "audio":
        return "bestaudio/best"
    h = "" if quality == "Mejor disponible" else f"[height<={int(quality.rstrip('p'))}]"
    if has_ffmpeg:
        return (
            f"bv{h}[ext=mp4]+ba[ext=m4a]/"
            f"bv{h}+ba/"
            f"b{h}[ext=mp4]/b{h}"
        )
    return f"b{h}[ext=mp4]/b{h}"


def extract_metadata(info: dict) -> dict:
    """Subset publicable de los metadatos, nunca cookies ni headers."""
    source = info or {}
    if source.get("_type") in ("playlist", "multi_video"):
        entries = source.get("entries") or []
        source = next((x for x in entries if isinstance(x, dict)), {})
    thumbs = source.get("thumbnails") or []
    thumbnail = source.get("thumbnail") or ""
    if not thumbnail and thumbs:
        thumbnail = next((x.get("url") for x in reversed(thumbs) if isinstance(x, dict) and x.get("url")), "")
    return {
        "title": str(source.get("title") or "Contenido sin título")[:240],
        "uploader": str(source.get("uploader") or source.get("channel") or "")[:140],
        "duration": int(source["duration"]) if isinstance(source.get("duration"), (int, float)) and source["duration"] >= 0 else None,
        "thumbnail": thumbnail if isinstance(thumbnail, str) and thumbnail.startswith("https://") else "",
        "id": str(source.get("id") or "")[:120],
    }


class _SilentLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class MediaEngine:
    def probe(self, url: str) -> dict:
        url = validate_url(url)
        ytdlp = get_ytdlp()
        options = {
            "quiet": True, "no_warnings": True, "noplaylist": True,
            "skip_download": True, "logger": _SilentLogger(),
            "socket_timeout": 25, "retries": 2, "extract_flat": False,
        }
        with ytdlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise RuntimeError("El sitio no proporcionó información del contenido.")
        return extract_metadata(info)

    def download(self, job: DownloadJob, directory: Path,
                 event: Callable[[str, dict], None], cancelled: Event) -> dict:
        ytdlp = get_ytdlp()
        directory.mkdir(parents=True, exist_ok=True)
        ffmpeg = ffmpeg_path()
        if job.kind == "audio" and not ffmpeg:
            raise EngineUnavailable("Para crear archivos MP3 debes instalar FFmpeg. Consulta README.md.")
        if cancelled.is_set():
            raise JobCancelled("Descarga cancelada")
        last_emit = 0.0

        def progress(data):
            nonlocal last_emit
            if cancelled.is_set():
                raise JobCancelled("Descarga cancelada por el usuario")
            status = data.get("status")
            if status == "finished":
                event("state", {"state": "procesando", "progress": 100.0})
                return
            if status != "downloading":
                return
            now = time.monotonic()
            if now - last_emit < 0.20:
                return
            last_emit = now
            have = data.get("downloaded_bytes") or 0
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            event("progress", {
                "downloaded": int(have),
                "total": int(total) if total else None,
                "progress": min(100.0, 100 * have / total) if total else 0.0,
                "speed": data.get("speed"),
                "eta": data.get("eta"),
            })

        def postproc(data):
            if cancelled.is_set():
                raise JobCancelled("Descarga cancelada por el usuario")
            event("state", {"state": "procesando", "progress": 100.0})

        options = {
            "quiet": True, "no_warnings": True, "noplaylist": True,
            "logger": _SilentLogger(), "windowsfilenames": True,
            "outtmpl": "%(title).160B [%(id)s].%(ext)s",
            "paths": {"home": str(directory)},
            "format": format_expression(job.kind, job.quality, bool(ffmpeg)),
            "continuedl": True,
            "overwrites": False,
            "retries": 3, "fragment_retries": 3,
            "socket_timeout": 30,
            "progress_hooks": [progress],
            "postprocessor_hooks": [postproc],
            "concurrent_fragment_downloads": 1,
            "restrictfilenames": False,
        }
        if ffmpeg:
            options["ffmpeg_location"] = ffmpeg
        if job.kind == "audio":
            options["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
                {"key": "FFmpegMetadata"},
            ]
        else:
            if ffmpeg:
                options["merge_output_format"] = "mp4"
                options["postprocessors"] = [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}]

        event("state", {"state": "descargando"})
        with ytdlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(job.url, download=True)
            if not info:
                raise RuntimeError("No se recibió información tras descargar.")
            name = Path(ydl.prepare_filename(info))
        if cancelled.is_set():
            raise JobCancelled("Descarga cancelada por el usuario")
        meta = extract_metadata(info)
        final_path = self._find_file(info, name, directory, job.kind)
        return {**meta, "file_path": str(final_path) if final_path else ""}

    @staticmethod
    def _find_file(info: dict, prepared: Path, directory: Path, kind: str) -> Path | None:
        candidates = []
        for key in ("filepath", "_filename"):
            if isinstance(info.get(key), str):
                candidates.append(Path(info[key]))
        downloads = info.get("requested_downloads") or []
        for row in downloads:
            if isinstance(row, dict) and row.get("filepath"):
                candidates.append(Path(row["filepath"]))
        candidates += [prepared, prepared.with_suffix(".mp3" if kind == "audio" else ".mp4")]
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() not in {".part", ".ytdl"}:
                if kind == "audio" and candidate.suffix.lower() != ".mp3":
                    continue
                return candidate
        ident = str(info.get("id") or "")
        if ident:
            try:
                matches = [p for p in directory.glob("*.*") if f"[{ident}]" in p.name and p.suffix.lower() not in {".part", ".ytdl"}]
                if kind == "audio":
                    matches = [p for p in matches if p.suffix.lower() == ".mp3"]
                if matches:
                    return max(matches, key=lambda p: p.stat().st_mtime)
            except OSError:
                return None
        return None
