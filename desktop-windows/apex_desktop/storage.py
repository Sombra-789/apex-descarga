"""Preferencias e historial privados, escritos de manera atómica."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import DownloadJob, THEMES, is_hex_color

MAX_HISTORY = 150


def user_data_dir() -> Path:
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
        return Path(root) / "ApexDescargaDesktop"
    root = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(root) / "ApexDescargaDesktop"


def default_download_dir() -> Path:
    return Path.home() / "Downloads" / "Apex Descarga"


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    draft = path.with_name(path.name + ".tmp")
    try:
        draft.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        draft.replace(path)
    finally:
        if draft.exists():
            draft.unlink()


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return fallback


class AppStore:
    def __init__(self, base: Path | None = None):
        self.base = base or user_data_dir()
        self.base.mkdir(parents=True, exist_ok=True)
        raw = load_json(self.base / "settings.json", {})
        self.settings: dict = {
            "folder": str(default_download_dir()),
            "theme": "Violeta",
            "accent": THEMES["Violeta"],
            "show_logo": True,
            "compact_mode": False,
        }
        if isinstance(raw, dict):
            self.settings.update({k: raw[k] for k in self.settings if k in raw})
        if self.settings["theme"] not in THEMES:
            self.settings["theme"] = "Violeta"
        if not is_hex_color(self.settings["accent"]):
            self.settings["accent"] = THEMES[self.settings["theme"]]
        if not isinstance(self.settings["folder"], str) or not self.settings["folder"].strip():
            self.settings["folder"] = str(default_download_dir())
        self.settings["show_logo"] = bool(self.settings["show_logo"])
        self.settings["compact_mode"] = bool(self.settings["compact_mode"])
        self.jobs: list[DownloadJob] = []
        jobs_data = load_json(self.base / "jobs.json", [])
        if isinstance(jobs_data, list):
            for row in jobs_data[-MAX_HISTORY:]:
                if not isinstance(row, dict):
                    continue
                try:
                    job = DownloadJob.from_dict(row)
                    if job.state in ("pendiente", "analizando", "descargando", "procesando"):
                        job.state = "interrumpido"
                        job.error = "La aplicación se cerró antes de terminar; pulsa Reintentar."
                    self.jobs.append(job)
                except (ValueError, TypeError):
                    continue

    def save_settings(self):
        atomic_json(self.base / "settings.json", self.settings)

    def save_jobs(self):
        atomic_json(self.base / "jobs.json", [j.to_dict() for j in self.jobs[-MAX_HISTORY:]])

    def add_job(self, job: DownloadJob):
        self.jobs.append(job)
        self.jobs = self.jobs[-MAX_HISTORY:]
        self.save_jobs()

    def get_job(self, job_id: str) -> DownloadJob | None:
        return next((x for x in self.jobs if x.id == job_id), None)

    def folder(self) -> Path:
        return Path(self.settings["folder"]).expanduser()
