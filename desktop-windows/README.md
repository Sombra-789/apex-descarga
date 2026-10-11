# Apex Descarga Desktop 0.1 — Windows 11

Aplicación **independiente** para descargar multimedia propia o autorizada desde Windows 11, desarrollada por **Apex Visual Studio**. No necesita tener Brave abierto, no accede automáticamente a cookies del navegador ni ejecuta un servidor web de Apex.

## Funciones de esta primera beta

- Diseño oscuro con navegación lateral: **Inicio, Cola, Biblioteca y Ajustes**.
- Enlaces HTTP(S) explícitos, análisis de título, autor, duración y portada cuando el sitio la proporciona.
- Descarga de **MP4** (calidad preferida, sujeto a formatos reales) y conversión de audio a **MP3**.
- Cola **secuencial**, porcentaje, velocidad y tiempo estimado, cancelación y reintento.
- Historial guardado localmente y recuperación manual de tareas interrumpidas.
- Abrir archivos y carpetas, carpeta de destino personalizable, 5 paletas de colores y HEX libre.
- Biblioteca con búsqueda por título/autor, motor yt-dlp incluido al compilar el `.exe`.
- No recopila telemetría propia, ni necesita cuenta.

## Requisitos

**Windows 11**, Python **3.11, 3.12 o 3.13** para ejecutar el código fuente (preferimos 3.12 o 3.13), conexión a Internet y **FFmpeg** para convertir audio a MP3 o unir video HD. Asegúrate de tener `ffmpeg.exe` en el `PATH`; también puede estar en `bin/ffmpeg.exe` junto al programa o `.exe`. Para ciertos sitios (incluido YouTube), yt-dlp puede requerir **Deno** y soporte JS actualizado; consulta la [documentación de yt-dlp](https://github.com/yt-dlp/yt-dlp).

Puedes reutilizar el FFmpeg y Deno ya instalados en tu PC para Apex Descarga Brave.

## Iniciar sin compilar

1. Descomprime este ZIP y conserva todas las carpetas.
2. Ejecuta `INICIAR_APEX.cmd` (sin permisos de administrador).
3. El script detecta Python compatible, crea el entorno `.venv` aislado e instala `yt-dlp` y `Pillow`.
4. Aparecerá la ventana de **Apex Descarga Desktop**. Pega un enlace, pulsa **Analizar enlace** y **Agregar a la cola**.
5. Para MP3 y video de múltiples pistas, verifica FFmpeg en Ajustes.

El código también puede iniciarse manualmente con `python main.py` después de instalar `requirements.txt`.

## Generar un ejecutable Windows `.exe`

1. Ejecuta primero `INICIAR_APEX.cmd` para que el entorno esté preparado.
2. Cierra la aplicación y ejecuta `BUILD_EXE_WINDOWS.cmd`.
3. Encontrarás el archivo **`dist/ApexDescargaDesktop.exe`** cuando PyInstaller termine.
4. El `.exe` contiene Python, la GUI y el módulo yt-dlp; **FFmpeg/Deno no se incluyen**. Deben instalarse por separado si el sitio o formato los requiere.
5. Comprueba el `.exe` con Windows Defender y pruébalo antes de distribuirlo a otras personas. Es una beta sin firma de código Windows.

**No está firmado con certificado Authenticode.** Windows SmartScreen puede mostrar advertencias por tratarse de un ejecutable nuevo. No desactives protecciones generales; distribuye solamente archivos que hayas compilado y verificado.

## Privacidad

Configuración e historial se guardan en `%LOCALAPPDATA%\ApexDescargaDesktop\`. Las miniaturas se solicitan al origen y yt-dlp establece conexión con la plataforma facilitada por el usuario; no existe un servidor de telemetría Apex en el código fuente. El usuario debe disponer de derechos o autorización sobre el contenido. No se implementa evasión de DRM ni se prometen descargas de fuentes protegidas.

Para eliminar el historial local, cierra la aplicación y elimina `jobs.json` de la carpeta anterior. Esto **no borra** tus medios descargados.

## Limitaciones conocidas

- No soporta listas de reproducción ni descargas concurrentes: evita sorpresas de consumo y limita carga de CPU.
- Cerrar la aplicación detiene las descargas; no continúa en segundo plano después de salir.
- La cancelación puede esperar a que termine el procesamiento FFmpeg. Las transferencias parciales de yt-dlp pueden permanecer como `.part` para continuar al reintentar, si el origen lo permite.
- No existe selector de subtítulos, conversor local universal, login o sincronización con Android.
- Un MP4 1080p puede requerir unir flujos mediante FFmpeg; cuando no está disponible se intenta una fuente MP4 progresiva de calidad inferior.
- La biblioteca registra archivos creados por Apex; no recorre otras carpetas ni elimina archivos automáticamente.
- **Es una primera beta; todavía falta probarla en Windows 11**, por lo que no se considera una versión estable.

## Soporte y sugerencias

**angelrlpz030207@gmail.com** — incluye versión, Windows, pasos del error y captura del mensaje. No incluyas contraseñas, cookies, tokens ni enlaces privados.

Código del proyecto principal: https://github.com/Sombra-789/apex-descarga

## Licencias de terceros

- `yt-dlp`: Unlicense — https://github.com/yt-dlp/yt-dlp
- `Pillow`: HPND — https://python-pillow.github.io/pillow-wheels/ ; https://github.com/python-pillow/Pillow/blob/main/LICENSE
- `PyInstaller`: GPL con excepción específica para bootloader; consultar sus licencias.
- `FFmpeg`: LGPL/GPL según configuración del binario usado (no distribuido aquí).

Antes de publicar el `.exe`, revisar obligatoriamente licencias de todos los binarios incorporados, código y recursos de marca. El código de Apex se ofrece bajo los términos del repositorio original; su logotipo sigue sujeto a las condiciones de uso de marca del propietario.
