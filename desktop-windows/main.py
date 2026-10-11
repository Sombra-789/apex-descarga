"""Punto de entrada de Apex Descarga Desktop."""
import sys
from pathlib import Path


def self_check() -> int:
    """Comprobación no gráfica para validar el EXE empaquetado en CI."""
    from apex_desktop.engine import get_ytdlp
    from apex_desktop.ui_pro import DesktopApp
    from apex_desktop.models import validate_url
    import PIL
    get_ytdlp()
    validate_url("https://example.com/media")
    if not issubclass(DesktopApp, __import__("tkinter").Tk):
        raise RuntimeError("La interfaz 0.2 UI Pro no está disponible")
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    if not (root / "assets" / "apex_icon.png").is_file():
        raise RuntimeError("Faltan recursos de la marca Apex")
    return 0


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        try:
            raise SystemExit(self_check())
        except Exception:
            # PyInstaller --windowed no dispone de consola para ver el traceback.
            import traceback
            Path("self-check-error.txt").write_text(traceback.format_exc(), encoding="utf-8")
            raise SystemExit(1)
    if "--version" in sys.argv:
        from apex_desktop import __version__
        print(f"Apex Descarga Desktop {__version__}")
        raise SystemExit(0)
    from apex_desktop.ui_pro import DesktopApp
    DesktopApp().mainloop()
