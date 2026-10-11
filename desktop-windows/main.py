"""Punto de entrada de Apex Descarga Desktop."""
import sys
from pathlib import Path


def self_check() -> int:
    """Comprobación no gráfica para validar el EXE empaquetado en CI."""
    from apex_desktop.engine import get_ytdlp
    from apex_desktop.models import validate_url
    import PIL
    get_ytdlp()
    validate_url("https://example.com/media")
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    if not (root / "assets" / "apex_icon.png").is_file():
        raise RuntimeError("Faltan recursos de la marca Apex")
    return 0


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        raise SystemExit(self_check())
    if "--version" in sys.argv:
        from apex_desktop import __version__
        print(f"Apex Descarga Desktop {__version__}")
        raise SystemExit(0)
    from apex_desktop.ui import DesktopApp
    DesktopApp().mainloop()
