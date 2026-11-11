# Compatibilidad y límites

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
