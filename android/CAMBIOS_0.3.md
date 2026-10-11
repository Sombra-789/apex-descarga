# Cambios 0.3.0 (beta)

- Branding de Apex Visual Studio; eliminado el borde del logotipo en la cabecera y opción de ocultarlo.
- Cinco temas predefinidos, más personalización HEX de tres colores, persistidos localmente.
- Vista previa mejorada con título, duración, resoluciones (cuando existan) y miniatura de tamaño limitado.
- Descarga por cola con estados persistentes, cancelación y reintentos de formato para MP4.
- Servicio en primer plano de Android con progreso en notificaciones, ejecuta los trabajos de uno en uno.
- Registro de resultados en biblioteca; abrir, compartir y eliminar medios guardados.
- Conversión local mediante herramientas del sistema: extracción AAC→M4A y recorte compatible MP4 sin recodificar (experimental).
- Actualización automática de yt-dlp estable cada ~7 días en red no medida, si el usuario la deja activada; configurable.
- Permisos agregados: servicio en primer plano para transferencia y notificaciones (solicitud opcional en Android 13+). No se solicita almacenamiento global.
- Mismo `applicationId`; `versionCode=4` y `versionName=0.3.0`.

## No incluido todavía

- Descargas paralelas, pausa/reanudación exacta a mitad de un archivo.
- Conversión local a MP3, edición avanzada con FFmpeg, importación automática de archivos anteriores.
- Generación del APK dentro de este entorno (sin Android SDK).
