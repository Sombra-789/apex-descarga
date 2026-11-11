# Compatibilidad y límites

## Limitaciones actuales

- **No admite todos los sitios ni todos los enlaces.** La disponibilidad depende del sitio de origen y del motor de descarga; un servicio puede dejar de funcionar si cambia.
- **Threads no está soportado por ahora en Windows 1.2.4.** Apex muestra un aviso antes de intentar descargar.
- **No es un descargador general de archivos.** Su objetivo es guardar video y audio compatibles, no texto, imágenes o documentos de cualquier página.
- **La calidad depende de la fuente.** Elegir una resolución alta no mejora un video que originalmente tiene menor calidad.
- **MP3 y combinación de audio/video requieren FFmpeg.** Sin esa herramienta, algunas opciones no estarán disponibles.
- **No inicia sesión con cookies del navegador ni evita las protecciones DRM.** El contenido privado o que exige acceso puede no descargarse.
- **No descarga listas de reproducción.** En Windows procesa un trabajo a la vez; el navegador debe permanecer abierto.
- **Apex en Chrome y Edge (Windows):** la extensión comparte la base Chromium con Brave. Su instalación y conexión con el programa de Windows aún requieren pruebas manuales completas en esos navegadores; la advertencia se refiere al soporte de Apex, no a los navegadores.
- **Apex para Android:** es una aplicación móvil independiente en versión Preview (de pruebas). No es una extensión de Chrome o Edge y sus actualizaciones se publican por separado.
- **Las pruebas son limitadas.** Windows 1.2.4 aún necesita aceptación manual completa en Brave; no se garantiza funcionamiento en todos los equipos o sitios.

## Abierto a futuras actualizaciones

**Apex Descarga sigue abierto a futuras actualizaciones.** Pueden evaluarse correcciones de errores, mejoras de compatibilidad, ajustes de instalación y facilidad de uso, y nuevas funciones según las necesidades de los usuarios y las pruebas realizadas.

Las sugerencias se reciben en **[apexsoftware.inc07@gmail.com](mailto:apexsoftware.inc07@gmail.com)**. Una propuesta no implica que ya esté en desarrollo: por ahora no se anuncian funciones ni fechas de publicación comprometidas.

## Windows 1.2.4

«Pestaña actual» copia enlaces HTTP(S). Aceptar una dirección no garantiza una descarga: el análisis y la extracción dependen de yt-dlp y del sitio. Usa el enlace a un contenido concreto.

| Contenido | Comportamiento |
| --- | --- |
| Video o audio de un sitio compatible con yt-dlp | Se intenta analizar o descargar en MP4/MP3 |
| Threads (`threads.com`, `threads.net` y subdominios) | Sin soporte por ahora; aviso antes de analizar, encolar o descargar |
| Página principal, canal o colección | No garantiza contenido descargable; las listas no están habilitadas |
| Texto, imágenes, documentos u otros archivos | No se ofrece un descargador general de archivos |
| Contenido que exige iniciar sesión o DRM | Apex no obtiene cookies ni inicia sesión; no elude DRM |

Aviso para Threads: «Las descargas de Threads todavía no están disponibles en Apex Descarga.» El componente local aplica la misma regla aunque la petición no proceda del popup; la cola guardada también se comprueba al procesarla.

El soporte de Threads se reconsiderará cuando exista una solución que podamos probar con publicaciones representativas. [Solicitud upstream de yt-dlp](https://github.com/yt-dlp/yt-dlp/issues/7523).

## Instalación coherente

Extensión y componente local deben ser de la misma versión. Los instaladores comprueban el paquete antes de copiarlo. No mezcles archivos de carpetas o ZIP antiguos; `windows/validate-package.ps1` y `scripts/package_windows.py` verifican la coherencia de versión. La configuración de destino y las autorizaciones del navegador se conservan al actualizar.

Estas reglas corresponden a Windows 1.2.4. Android mantiene su propia versión y no recibe estos cambios automáticamente.
