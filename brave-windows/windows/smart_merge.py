"""Apex Smart Merge Engine 2.0 alpha.1.

Public MediaFire file links -> bounded, resumable RAR part downloads -> 7-Zip test,
extract and repack. Local execution only. Does not change the MP4/MP3 engine.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

MAX_LINKS = 100
MAX_TOTAL = 16 * 1024 ** 3
MAX_PART = 8 * 1024 ** 3
MAX_UNPACKED = 16 * 1024 ** 3
CHUNK = 256 * 1024
RAR = re.compile(r"^(?P<base>.+?)\.part(?P<number>\d{1,3})\.rar$", re.I)
KNOWN = ("mediafire.com",)
UA = "ApexDescargaSmartMerge/2.0 (Windows; authorized-public-downloads)"
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10))}


class MergeError(ValueError):
    pass


class Cancelled(MergeError):
    pass


def host_allowed(host: str) -> bool:
    host = host.lower().rstrip(".")
    return any(host == domain or host.endswith("." + domain) for domain in KNOWN)


def check_url(raw: str, *, resolve_dns: bool = False) -> str:
    if not isinstance(raw, str) or not 10 <= len(raw.strip()) <= 2000:
        raise MergeError("Introduce enlaces MediaFire válidos (HTTPS).")
    url = raw.strip()
    if any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise MergeError("El enlace contiene caracteres no permitidos.")
    try:
        parsed = urllib.parse.urlsplit(url)
        host = parsed.hostname or ""
        if (parsed.scheme != "https" or not host_allowed(host) or
                parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise MergeError("Solo se permiten enlaces públicos HTTPS de MediaFire en esta Alpha.")
    except ValueError as exc:
        raise MergeError("URL o puerto no válido.") from exc
    if resolve_dns:
        try:
            addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
                raise MergeError("El dominio se resuelve a una red privada o reservada.")
        except (OSError, ValueError) as exc:
            raise MergeError("No se pudo validar la dirección del servidor MediaFire.") from exc
    return url


def filename_from_link(url: str) -> str:
    parts = [urllib.parse.unquote(p) for p in urllib.parse.urlsplit(url).path.split("/") if p]
    # MediaFire public page: /file/<public-id>/<filename>/file
    if len(parts) >= 4 and parts[0] == "file" and parts[-1] == "file":
        result = parts[-2]
    else:
        result = parts[-1] if parts else ""
    if not result or result in (".", "..") or "/" in result or "\\" in result or "\0" in result:
        raise MergeError("El enlace no incluye un nombre RAR identificable.")
    forbidden = set('<>:"|?*')
    if (any(char in forbidden or ord(char) < 32 for char in result)
            or result.rstrip(" .") != result or result.split(".")[0].upper() in RESERVED):
        raise MergeError("El nombre RAR contiene caracteres no válidos para Windows.")
    return result


def analyze(urls) -> dict:
    if not isinstance(urls, list) or not 2 <= len(urls) <= MAX_LINKS:
        raise MergeError("Pega entre 2 y 100 enlaces, uno por línea.")
    parts, numbers, groups, seen_urls, widths = [], set(), set(), set(), set()
    duplicates = []
    for raw in urls:
        url = check_url(raw)
        name = filename_from_link(url)
        match = RAR.fullmatch(name)
        if not match:
            raise MergeError(f"No se reconoce {name[:90]}: usa nombres nombre.part01.rar, part02.rar...")
        base = match["base"]
        if not base or base.endswith(".") or len(base) > 130:
            raise MergeError("Nombre base de archivo inválido o demasiado largo.")
        number = int(match["number"])
        widths.add(len(match["number"]))
        if number < 1 or number > 100:
            raise MergeError("Numeración de partes fuera de 1 a 100.")
        if number in numbers or url in seen_urls:
            duplicates.append(number)
        numbers.add(number)
        groups.add(base.casefold())
        seen_urls.add(url)
        parts.append({"url": url, "name": name, "number": number})
    if len(groups) != 1:
        raise MergeError("Las partes no pertenecen al mismo archivo base.")
    if len(widths) != 1:
        raise MergeError("La numeración de las partes tiene distintos rellenos (part1, part02). Debe ser uniforme.")
    if duplicates:
        raise MergeError("Partes repetidas: " + ", ".join(map(str, sorted(set(duplicates)))))
    missing = sorted(set(range(1, max(numbers) + 1)) - numbers)
    if missing:
        raise MergeError("Faltan partes: " + ", ".join(map(str, missing[:20])))
    return {"ok": True, "type": "smart_analysis",
            "base": parts[0]["name"][:parts[0]["name"].lower().rfind(".part")],
            "parts": sorted(parts, key=lambda item: item["number"]),
            "count": len(parts), "provider": "MediaFire"}


class _DownloadLink(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.href = ""
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        values = dict(attrs)
        if values.get("id") == "downloadButton" and values.get("href"):
            self.href = values["href"]


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.count = 0
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        if self.count > 5:
            raise MergeError("Demasiadas redirecciones del proveedor.")
        check_url(newurl, resolve_dns=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(url, headers=None, timeout=35):
    check_url(url, resolve_dns=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _SafeRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity",
                                                  **(headers or {})})
    response = opener.open(request, timeout=timeout)
    try:
        check_url(response.geturl(), resolve_dns=True)
        return response
    except Exception:
        response.close()
        raise


def resolve_public_file(url: str) -> str:
    """Resolve only the public download button; never automate cookies/challenges."""
    parsed = urllib.parse.urlsplit(check_url(url))
    if not (parsed.hostname or "").lower().endswith("mediafire.com") or not parsed.path.startswith("/file/"):
        return url
    with _open(url) as response:
        mime = response.headers.get("Content-Type", "").lower()
        if "html" not in mime:
            raise MergeError("El enlace de MediaFire ya no entrega una página pública esperada.")
        html = response.read(1_000_001)
        if len(html) > 1_000_000:
            raise MergeError("La página de MediaFire es demasiado grande.")
        parser = _DownloadLink()
        parser.feed(html.decode("utf-8", "replace"))
    if not parser.href:
        raise MergeError("MediaFire no ofreció un enlace público directo; enlace caducado, privado o requiere navegador.")
    return check_url(urllib.parse.urljoin(url, parser.href), resolve_dns=True)


def _hash_file(file: Path) -> str:
    sha = hashlib.sha256()
    with file.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            sha.update(block)
    return sha.hexdigest()


def _write_json(file: Path, payload: dict):
    temp = file.with_name(file.name + ".tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.replace(temp, file)
    finally:
        if temp.exists():
            temp.unlink()


def _read_json(file: Path) -> dict:
    try:
        result = json.loads(file.read_text(encoding="utf-8"))
        return result if isinstance(result, dict) else {}
    except (OSError, ValueError):
        return {}


class Progress:
    def __init__(self, count, callback):
        self.count, self.callback = count, callback
        self.lock = threading.Lock()
        self.bytes = {}
        self.expected = {}
        self.completed = set()
        self.last_emit = 0.0
        self.start = time.monotonic()
    def update(self, num, received, expected=None, *, done=False):
        with self.lock:
            self.bytes[num] = received
            if expected is not None:
                self.expected[num] = expected
            if done:
                self.completed.add(num)
            now = time.monotonic()
            if now - self.last_emit < 0.6 and not done:
                return
            self.last_emit = now
            consumed = sum(self.bytes.values())
            if consumed > MAX_TOTAL:
                raise MergeError("El conjunto excedió el límite total de 16 GiB.")
            total = sum(self.expected.values()) if len(self.expected) == self.count else None
            speed = consumed / max(0.1, now - self.start)
            # 0..70% is download stage. Without every Content-Length, percent is unknown.
            percent = round(70 * consumed / total, 1) if total else None
            eta = (total - consumed) / speed if total and speed else None
            event = {"type": "progress", "stage": "download", "percent": percent,
                     "bytes_received": consumed, "bytes_total": total,
                     "speed_bps": round(speed), "eta_seconds": round(eta) if eta is not None else None,
                     "parts_done": len(self.completed), "parts_total": self.count,
                     "message": f"Descargando partes: {len(self.completed)}/{self.count}"}
        self.callback(event)


def _download_one(part, work: Path, cancel: threading.Event, progress: Progress):
    num = part["number"]
    target = work / part["name"]
    partial = work / (part["name"] + ".partial")
    done_meta = work / (part["name"] + ".verified.json")
    resume_meta = work / (part["name"] + ".resume.json")
    fingerprint = hashlib.sha256(part["url"].encode()).hexdigest()
    completed = _read_json(done_meta)
    if (target.is_file() and completed.get("fingerprint") == fingerprint and
            completed.get("size") == target.stat().st_size and
            completed.get("sha256") == _hash_file(target)):
        progress.update(num, target.stat().st_size, target.stat().st_size, done=True)
        return target
    for file in (done_meta, target):
        file.unlink(missing_ok=True)
    last_error = ""
    for attempt in range(1, 4):
        if cancel.is_set():
            raise Cancelled("Operación cancelada.")
        try:
            download_url = resolve_public_file(part["url"])
            previous = _read_json(resume_meta)
            offset = partial.stat().st_size if partial.exists() else 0
            can_resume = (offset > 0 and previous.get("fingerprint") == fingerprint and
                          previous.get("url") == download_url and
                          (previous.get("etag") or previous.get("modified")) and
                          offset < int(previous.get("total") or MAX_PART))
            if not can_resume:
                offset = 0
                partial.unlink(missing_ok=True)
            headers = {}
            if can_resume:
                headers["Range"] = f"bytes={offset}-"
                headers["If-Range"] = previous.get("etag") or previous["modified"]
            with _open(download_url, headers) as response:
                mime = response.headers.get("Content-Type", "").lower()
                if "html" in mime:
                    raise MergeError("El proveedor devolvió HTML en lugar de una parte RAR (enlace caducado o acceso restringido).")
                status = getattr(response, "status", 200)
                content_length = response.headers.get("Content-Length", "")
                length = int(content_length) if content_length.isdigit() else None
                if can_resume and status == 206:
                    content_range = response.headers.get("Content-Range", "")
                    if not content_range.startswith(f"bytes {offset}-"):
                        raise MergeError("El servidor devolvió un rango inconsistente.")
                    mode = "ab"
                elif can_resume:
                    offset = 0
                    mode = "wb"
                else:
                    mode = "wb"
                total = (offset + length) if length is not None else None
                if total is not None and total > MAX_PART:
                    raise MergeError("Parte demasiado grande: límite de 8 GiB.")
                validators = {"fingerprint": fingerprint, "url": download_url, "total": total,
                              "etag": response.headers.get("ETag", ""),
                              "modified": response.headers.get("Last-Modified", "")}
                _write_json(resume_meta, validators)
                received = offset
                with partial.open(mode) as file:
                    while True:
                        if cancel.is_set():
                            raise Cancelled("Operación cancelada.")
                        block = response.read(CHUNK)
                        if not block:
                            break
                        received += len(block)
                        if received > MAX_PART:
                            raise MergeError("Parte excedió el límite de 8 GiB.")
                        file.write(block)
                        progress.update(num, received, total)
                if total is not None and received != total:
                    raise MergeError("Descarga incompleta: tamaño recibido distinto al anunciado.")
            if partial.stat().st_size < 8:
                raise MergeError("Parte vacía o incompleta.")
            with partial.open("rb") as file:
                if not file.read(7).startswith(b"Rar!\x1a\x07"):
                    raise MergeError("El enlace no devolvió un volumen RAR válido.")
            os.replace(partial, target)
            _write_json(done_meta, {"fingerprint": fingerprint, "size": target.stat().st_size,
                                    "sha256": _hash_file(target)})
            resume_meta.unlink(missing_ok=True)
            progress.update(num, target.stat().st_size, target.stat().st_size, done=True)
            return target
        except Cancelled:
            raise
        except (OSError, urllib.error.URLError, MergeError, ValueError) as error:
            last_error = str(error)
            if attempt < 3:
                time.sleep(attempt)
    raise MergeError(f"Parte {num:02d}: {last_error}")


def find_7zip() -> str:
    for name in ("7z", "7zz", "7za"):
        found = shutil.which(name)
        if found:
            return found
    if os.name == "nt":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            base = os.environ.get(variable)
            if base:
                candidate = Path(base) / "7-Zip" / "7z.exe"
                if candidate.is_file():
                    return str(candidate)
    raise MergeError("Falta 7-Zip (7z.exe). Instálalo desde 7-zip.org y vuelve a intentar.")


def _process(command, cancel: threading.Event, *, cwd=None, timeout=3600, capture=False) -> str:
    with tempfile.TemporaryFile(mode="w+b") as log:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        process = subprocess.Popen(command, cwd=cwd, shell=False, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
        start = time.monotonic()
        while process.poll() is None:
            if cancel.is_set() or time.monotonic() - start > timeout:
                process.kill()
                process.wait(timeout=10)
                if cancel.is_set():
                    raise Cancelled("Operación cancelada.")
                raise MergeError("7-Zip superó el tiempo permitido.")
            time.sleep(0.15)
        log.seek(0)
        output = log.read(4_000_001).decode("utf-8", "replace")
        if len(output) > 4_000_000:
            raise MergeError("El archivo contiene demasiadas entradas o datos de listado.")
        if process.returncode != 0:
            low = output.lower()
            if "wrong password" in low or "password" in low or "encrypted" in low:
                raise MergeError("El archivo RAR necesita contraseña o la contraseña es incorrecta.")
            if "crc failed" in low or "data error" in low or "unexpected end" in low:
                raise MergeError("7-Zip detectó datos dañados o partes RAR incompletas.")
            raise MergeError(f"Error de 7-Zip ({process.returncode}): {output[-320:]}")
        return output if capture else ""


def _validate_members(text: str) -> tuple[int, int]:
    if "----------" not in text:
        raise MergeError("No se pudo leer el listado del archivo RAR.")
    members = re.split(r"\r?\n\s*\r?\n", text.split("----------", 1)[1])
    files, size = 0, 0
    for member in members:
        fields = dict(line.split(" = ", 1) for line in member.splitlines() if " = " in line)
        name = fields.get("Path", "").strip()
        if not name:
            continue
        normalized = name.replace("\\", "/")
        segments = normalized.split("/")
        win = PureWindowsPath(name)
        if (name.startswith(("/", "\\")) or win.is_absolute() or ":" in name or
                any(p in ("", ".", "..") or p.rstrip(" .").upper().split(".")[0] in RESERVED
                    for p in segments) or
                any(ord(c) < 32 for c in name)):
            raise MergeError("El archivo contiene rutas peligrosas o fuera de destino.")
        attrs = fields.get("Attributes", "")
        if "Symbolic Link" in member or attrs.startswith("l"):
            raise MergeError("El archivo contiene enlaces simbólicos no admitidos.")
        if fields.get("Folder") == "+":
            continue
        files += 1
        n = int(fields.get("Size", "0"))
        if n < 0:
            raise MergeError("El archivo contiene un tamaño inválido.")
        size += n
        if files > 10000 or size > MAX_UNPACKED:
            raise MergeError("El contenido excede límites de extracción seguros.")
    if files == 0:
        raise MergeError("El archivo RAR no contiene archivos para extraer.")
    return files, size


def _check_extracted(root: Path):
    entries = 0
    for current, directories, filenames in os.walk(root, followlinks=False):
        for name in directories + filenames:
            file = Path(current) / name
            if file.is_symlink():
                raise MergeError("La extracción creó un enlace simbólico no admitido.")
            if not file.resolve().is_relative_to(root.resolve()):
                raise MergeError("Se detectó una ruta fuera del directorio temporal.")
            entries += 1
            if entries > 20000:
                raise MergeError("Demasiados archivos extraídos.")


def _emit(callback, stage, message, percent=None, **more):
    callback({"type": "progress", "stage": stage, "message": message,
              "percent": percent, **more})


def execute(request: dict, callback, cancel: threading.Event, destination: Path) -> dict:
    manifest = analyze(request.get("urls"))
    parallel = request.get("parallel", 2)
    output_format = request.get("output", "zip")
    cleanup = request.get("cleanup", False)
    if type(parallel) is not int or not 1 <= parallel <= 4:
        raise MergeError("El paralelismo permitido es de 1 a 4.")
    if output_format not in ("zip", "7z") or type(cleanup) is not bool:
        raise MergeError("Formato o ajustes no válidos.")
    seven = find_7zip()
    directory = Path(destination).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise MergeError("La carpeta de salida no está disponible.")
    fingerprint = hashlib.sha256("\n".join(p["url"] for p in manifest["parts"]).encode()).hexdigest()[:20]
    work_root = directory / "SmartMerge_Work"
    result_dir = directory / "SmartMerge_Output"
    if work_root.is_symlink() or result_dir.is_symlink():
        raise MergeError("Las carpetas de trabajo y salida no son válidas.")
    workspace = work_root / fingerprint
    workspace.mkdir(parents=True, exist_ok=True)
    if workspace.is_symlink():
        raise MergeError("El directorio temporal no puede ser un enlace simbólico.")
    result_dir.mkdir(parents=True, exist_ok=True)
    _emit(callback, "analyze", f"{manifest['count']} partes detectadas y ordenadas", 0)
    progress = Progress(manifest["count"], callback)
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
        future_map = {pool.submit(_download_one, part, workspace, cancel, progress): part["number"]
                      for part in manifest["parts"]}
        try:
            for future in concurrent.futures.as_completed(future_map):
                if cancel.is_set():
                    raise Cancelled("Operación cancelada.")
                future.result()
        except Exception:
            cancel.set()
            pool.shutdown(wait=True, cancel_futures=True)
            raise
    if cancel.is_set():
        raise Cancelled("Operación cancelada.")
    if sum((workspace / p["name"]).stat().st_size for p in manifest["parts"]) > MAX_TOTAL:
        raise MergeError("Los volúmenes superan el límite de 16 GiB.")
    first = workspace / manifest["parts"][0]["name"]
    _emit(callback, "verify", "Comprobando el conjunto RAR con 7-Zip (CRC)", 72)
    listing = _process([seven, "l", "-slt", str(first)], cancel, capture=True, timeout=120)
    count, unpacked_size = _validate_members(listing)
    if shutil.disk_usage(directory).free < unpacked_size * 2 + 150 * 1024 * 1024:
        raise MergeError("No hay espacio disponible suficiente para extraer el contenido.")
    _process([seven, "t", "-y", "-bd", str(first)], cancel, timeout=3600)
    _emit(callback, "extract", "Verificación aprobada; reconstruyendo archivos", 83)
    extracted = workspace / "contenido_extraido"
    if extracted.exists():
        shutil.rmtree(extracted)  # This engine's dedicated workspace only.
    extracted.mkdir(parents=True)
    _process([seven, "x", "-y", "-bd", "-o" + str(extracted), str(first)], cancel,
             timeout=3600)
    _check_extracted(extracted)
    if not any(p.is_file() for p in extracted.rglob("*")):
        raise MergeError("7-Zip no produjo archivos extraídos.")
    _emit(callback, "pack", "Creando archivo único " + output_format.upper(), 94)
    safe_base = re.sub(r"[^A-Za-z0-9._-]", "_", manifest["base"])[:65].strip("._") or "Apex_Merge"
    final = result_dir / f"{safe_base}-{fingerprint}.{output_format}"
    if final.exists():
        final = result_dir / f"{safe_base}-{fingerprint}-{uuid.uuid4().hex[:8]}.{output_format}"
    # Keep the correct .zip / .7z suffix for the archiver, and publish only
    # after the archive has passed a complete integrity test.
    stage = result_dir / (".smartmerge-building-" + fingerprint)
    if stage.is_symlink():
        raise MergeError("La carpeta de empaquetado no es válida.")
    stage.mkdir(exist_ok=True)
    temporary = stage / f"{safe_base}-{fingerprint}.{output_format}"
    temporary.unlink(missing_ok=True)
    try:
        _process([seven, "a", "-y", "-bd", "-t" + output_format, "-mx=3",
                  str(temporary), "."], cancel, cwd=extracted, timeout=3600)
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise MergeError("No se creó el archivo unificado.")
        _emit(callback, "verify_output", "Verificando integridad del archivo único", 98)
        _process([seven, "t", "-y", "-bd", str(temporary)], cancel, timeout=3600)
        os.replace(temporary, final)
        digest = _hash_file(final)
        if not final.is_file() or final.stat().st_size == 0:
            raise MergeError("Falló la verificación del archivo final.")
    finally:
        temporary.unlink(missing_ok=True)
        try:
            stage.rmdir()
        except OSError:
            pass
    if cleanup:
        shutil.rmtree(workspace)
    return {"type": "done", "ok": True, "percent": 100, "stage": "done",
            "file": final.name, "path": str(final), "folder": str(result_dir),
            "sha256": digest, "files_inside": count, "cleanup": cleanup,
            "message": "Archivo único verificado. El resultado es local: no se creó un enlace web."}


def run_native(request, send, recv, destination):
    cancel = threading.Event()
    lock = threading.Lock()
    def emit(message):
        with lock:
            send(message)
    def listen():
        while not cancel.is_set():
            try:
                message = recv()
                if message is None or message.get("type") == "cancel":
                    cancel.set()
                    return
            except Exception:
                cancel.set()
                return
    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    try:
        answer = execute(request, emit, cancel, Path(destination))
        emit(answer)
    except Cancelled as exc:
        emit({"type": "done", "ok": False, "cancelled": True, "error": str(exc)})
    except Exception as exc:
        emit({"type": "error", "ok": False, "error": str(exc)[:420]})
