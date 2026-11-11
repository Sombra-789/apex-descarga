# Desarrollo y pruebas

El código Windows vive en `brave-windows/` y Android en `android/`. Cada edición mantiene su versión y estado de validación. Consulta [docs/README.md](docs/README.md) para localizar guías e historia.

Desde la raíz, con Python 3 y Node.js:

```powershell
node brave-windows/tests/test_extension.js
node brave-windows/tests/test_popup.js
py -3 -m unittest discover -s brave-windows/tests -p 'test_*.py' -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File brave-windows/windows/validate-package.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File brave-windows/tests/test_diagnostico.ps1
py -3 scripts/package_windows.py
```

El ZIP y su SHA-256 se generan en `dist/`, excluido de Git. Los tests no descargan medios. El flujo Windows también comprueba una primera instalación aislada sin registrar un navegador; esto no sustituye la prueba manual con Brave.

Al cambiar versión Windows, actualiza conjuntamente extensión, componente local, instaladores, validación del paquete y notas. No cambies las condiciones aceptadas si su contenido no cambió. No subas `settings.json`, historiales, cookies, entornos Python ni respaldos personales.

Las recetas históricas de publicación se guardan en `docs/archive/workflows/`. Los flujos activos están en `.github/workflows/`; el empaquetador vigente toma el número del manifiesto y lo contrasta con el componente local.
