# Compilar y descargar Apex Descarga Desktop 0.2 UI Pro

GitHub Actions usa un **runner Windows**, Python 3.12 y PyInstaller para generar un ejecutable independiente. El workflow también ejecuta pruebas y el autochequeo del `.exe` empaquetado.

1. [Abre las Actions de Desktop](https://github.com/Sombra-789/apex-descarga/actions/workflows/desktop-windows.yml).
2. Busca la ejecución verde cuyo commit incluya **0.2 UI Pro**.
3. Descarga el artefacto ZIP `ApexDescargaDesktop-0.2-Windows11-UI-PRO-BETA-NO-FIRMADO` desde **Artifacts**.
4. Extrae, analiza con Windows Defender y ejecuta `ApexDescargaDesktop.exe`. No necesitas Python instalado.
5. FFmpeg es necesario para MP3 o video de alta definición con audio separado; debe estar en `PATH` o en `bin` junto al ejecutable.
6. Si la app indica que falta el entorno JS, instala Deno desde su sitio oficial.

El `.exe` no está firmado digitalmente. Evita ignorar alertas inesperadas o desactivar Windows Defender. Reportes: **angelrlpz030207@gmail.com**.
