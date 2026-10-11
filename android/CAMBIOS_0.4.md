# Apex Descarga 0.4.0 — Vista previa y Media Queue

## Novedades

- **Portada real** obtenida del extractor yt-dlp (`getInfo`) cuando el sitio la proporcione; para enlaces públicos estándar de YouTube hay un respaldo por ID.
- **Caché privada de miniaturas** con comprobaciones HTTPS, host público, límite de 2 MB y redirecciones limitadas. Las imágenes no se reenvían a servidores de Apex.
- **Vista previa rediseñada** con miniatura, título, autor/canal, duración, plataforma y calidades comunicadas por el sitio.
- **Cola rediseñada** en pantalla independiente, tarjetas compactas con portada, título, autor, calidad, progreso y velocidad/ETA cuando esté disponible.
- **Acciones por estado:** cancelar (trabajos activos o esperando), reintentar (errores/cancelaciones/interrupciones), abrir archivo completado desde la cola.
- **Historial/biblioteca** con miniaturas, búsqueda, filtros de audio/video, abrir, compartir y eliminar.
- **Persistencia** de título, miniatura y detalles desde el análisis de enlace hasta el archivo final en la biblioteca.
- **Las descargas existentes de Apex 0.3 se conservan** si se actualiza la APK con la misma firma; las entradas antiguas pueden carecer de portada hasta un nuevo análisis. La biblioteca previa se mantiene.
- Mejoras visuales: bordes menos llamativos, superficies oscuras, colores de usuario en tarjetas y controles coherentes, logo sin borde.

## Sin cambios en el motor

- Se conservan la cola serial en servicio en primer plano, FFmpeg, yt-dlp, permisos mínimos, las cinco paletas y temas HEX personalizados, el logotipo opcional, la selección de calidades, MP3 y MP4.
- La actualización automática estable de yt-dlp permanece programada cuando el sistema la permite.
- El conversor local conserva su alcance experimental: AAC a M4A y recortes de MP4, **no** recodificación general a MP3.

## Limitaciones

- Algunas plataformas no proporcionan miniatura, autor, duración ni formatos. Si bloquean las solicitudes de imagen, aparece un icono neutro.
- La cola descarga **un enlace a la vez** por seguridad y uso eficiente de batería. "Reintentar" comienza desde el principio.
- El progreso y velocidad dependen de la información emitida por yt-dlp y pueden fluctuar durante la conversión o combinación de formatos.
- Solo contenido con permiso; sin bypass de DRM ni extracción de cookies/cuentas.
- **Código fuente beta**, sin compilación Android de esta revisión en el entorno de creación.
