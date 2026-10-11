"""Modelos puros y validación de entrada, sin dependencias de GUI."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

VALID_STATES = {
    "pendiente", "analizando", "descargando", "procesando", "completado",
    "error", "cancelado", "interrumpido",
}
FINISHED_STATES = {"completado", "error", "cancelado", "interrumpido"}
QUALITIES = ("Mejor disponible", "480p", "720p", "1080p", "1440p", "2160p")
THEMES = {
    "Violeta": "#A16BFA",
    "Cian": "#1BC8DB",
    "Azul Apex": "#3988FF",
    "Esmeralda": "#36D4AB",
    "Coral": "#F68D72",
}


def is_hex_color(value: str) -> bool:
    return isinstance(value, str) and len(value) == 7 and value[0] == "#" and all(c in "0123456789abcdefABCDEF" for c in value[1:])


def validate_url(value: str) -> str:
    """Aceptar solo URLs web públicas expresas. No elimina riesgos de sitios externos."""
    value = (value or "").strip()
    if len(value) > 4096:
        raise ValueError("El enlace es demasiado largo.")
    try:
        parsed = urlparse(value)
        host = parsed.hostname or ""
        port = parsed.port  # obliga a validar sintaxis de puerto
    except ValueError as exc:
        raise ValueError("La dirección web no es válida.") from exc
    if parsed.scheme.lower() not in ("http", "https") or not host:
        raise ValueError("Solo se admiten enlaces públicos http:// o https://.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("No incluyas contraseñas o usuarios dentro del enlace.")
    if host.lower() in {"localhost", "localhost.localdomain"} or host.lower().endswith((".local", ".internal")):
        raise ValueError("Solo se admiten enlaces públicos, no direcciones locales.")
    try:
        ip = ip_address(host)
        if not ip.is_global:
            raise ValueError("No se permiten direcciones IP privadas o reservadas.")
    except ValueError as exc:
        if "privadas" in str(exc):
            raise
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("El puerto del enlace no es válido.")
    return value


def display_bytes(value: float | int | None) -> str:
    if value is None:
        return "—"
    n = max(0, float(value))
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return "—"


def display_duration(seconds: float | int | None) -> str:
    if seconds is None:
        return "—"
    value = int(max(0, seconds))
    h, r = divmod(value, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


@dataclass
class DownloadJob:
    url: str
    kind: str = "video"  # video o audio
    quality: str = "1080p"
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str = "Contenido sin analizar"
    uploader: str = ""
    duration: int | None = None
    thumbnail: str = ""
    state: str = "pendiente"
    progress: float = 0.0
    speed: float | None = None
    eta: int | None = None
    downloaded: int = 0
    total: int | None = None
    file_path: str = ""
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        self.url = validate_url(self.url)
        if self.kind not in ("video", "audio"):
            raise ValueError("Formato de descarga no válido")
        if self.quality not in QUALITIES:
            raise ValueError("Calidad no válida")
        if self.state not in VALID_STATES:
            raise ValueError("Estado no válido")
        self.progress = min(100.0, max(0.0, float(self.progress)))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DownloadJob":
        allowed = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in allowed})

    @property
    def can_open(self) -> bool:
        return self.state == "completado" and bool(self.file_path) and Path(self.file_path).is_file()
