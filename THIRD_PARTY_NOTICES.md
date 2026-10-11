# Avisos de terceros / Third-party notices

## Componentes utilizados o requeridos

| Componente | Uso | Referencia | Licencia/obligación conocida |
|---|---|---|---|
| yt-dlp | Extracción de metadatos y medios | https://github.com/yt-dlp/yt-dlp | Unlicense (comprobar versión incluida) |
| youtubedl-android | Integración del motor en Android | https://github.com/yausername/youtubedl-android | GPL-3.0 (ver licencia concreta de `0.18.1`) |
| FFmpeg | Unión/conversión de medios | https://ffmpeg.org/legal.html | LGPL o GPL según componentes y configuración de cada binario; **no asumir una sola licencia** |
| Android/Gradle/JDK | Herramientas de compilación | https://developer.android.com/ | Licencias propias de sus distribuidores |
| Python/Deno | Motor local y entorno JS en Windows | https://www.python.org/ / https://deno.com/ | Licencias propias de cada distribución |

El repositorio incluye **código fuente de Apex** y recursos gráficos del proyecto; no redistribuye de forma intencional archivos binarios de bibliotecas Gradle, SDK ni FFmpeg. Al generar y distribuir una APK, ciertas bibliotecas y binarios sí se incorporan al instalable.

## Requisitos antes de distribuir el APK

1. Inspeccionar el árbol de dependencias de Gradle, los binarios empaquetados (incluida configuración real de FFmpeg) y licencias exactas.
2. Facilitar el texto íntegro de las licencias aplicables y avisos de copyright, así como el código fuente correspondiente exigido por GPL/LGPL cuando proceda.
3. Confirmar los requisitos de publicación y atribución de cualquier imagen/logo/icono; el logotipo Apex fue aportado por el propietario.
4. No afirmar que las bibliotecas de terceros son propiedad de Apex Visual Studio, ni sugerir afiliación con los servicios compatibles.
5. No distribuir el APK como release definitivo hasta completar auditoría, pruebas y firma.

Esto es una guía técnica, no asesoría jurídica.

## Anexo específico Brave/Windows 1.2.2

El paquete contiene scripts PowerShell para actualizar una instalación existente y abrir un selector de carpetas nativo, además de un pequeño launcher en C#. Se redistribuyen como código fuente de Apex. El motor Python usa yt-dlp instalado por separado y depende de FFmpeg y, según el sitio, yt-dlp-ejs/Deno. No se incluye en esta carpeta una copia de binarios de FFmpeg/yt-dlp.

Los avisos de privacidad y términos originales del paquete figuran en [`brave-windows/PRIVACIDAD_Y_CONDICIONES.md`](brave-windows/PRIVACIDAD_Y_CONDICIONES.md). Comprueba los avisos y las licencias vigentes de las dependencias antes de publicar.
