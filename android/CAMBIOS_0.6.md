# Apex Descarga Android 0.6 — UI Pro

- Diseño nativo inspirado en las cuatro pantallas de Figma (`tnVTpd2xcdL4XqrEuWmNUH`).
- Barra de navegación inferior persistente, con Inicio / Cola / Biblioteca / Ajustes.
- Pantalla Inicio simplificada: portada, metadatos, tipo MP4/MP3, calidad y acciones principales.
- Cola independiente con tarjetas compactas y progreso; biblioteca con búsqueda y acciones.
- Nueva SettingsActivity con las claves previas para colores HEX, tema, logo, Wi-Fi, tamaño, carpeta y actualizador yt-dlp.
- Conserva el logotipo original sin bordes, ocultable mediante preferencias.
- Conversor accesible desde Biblioteca y con navegación inferior.
- Actualización de versionName=0.6.0 y versionCode=7; packageId original conservado.
- Backend sin modificaciones: DownloadService, DownloadQueueStore, EngineUpdateJob, EngineHealth, MediaMetadata y DownloadStorage.

La UI en Figma y el código Android no son automáticamente sincronizados. La actualización es código nativo Java.
