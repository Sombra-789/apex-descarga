# Plan de pruebas Windows 11 — Apex Descarga Desktop 0.1

- [ ] Abrir desde INICIAR_APEX.cmd, sin Brave abierto.
- [ ] Probar enlace público autorizado YouTube: vista previa con miniatura, título y duración.
- [ ] Descargar MP4 720p y 1080p; comprobar codec, audio y duración de archivo.
- [ ] Descargar MP3; comprobar reproducción y bitrate.
- [ ] Poner tres enlaces en cola; confirmar orden, progreso, velocidad y ETA.
- [ ] Cancelar y reintentar un trabajo; verificar que el archivo final no quede corrupto.
- [ ] Cambiar carpeta destino, cerrar y reabrir, comprobar persistencia.
- [ ] Aplicar color HEX y paletas, comprobar persistencia después de cerrar/abrir.
- [ ] Probar biblioteca, búsqueda, botón abrir archivo y abrir carpeta.
- [ ] Simular pérdida de Internet y error de sitio no compatible; revisar mensajes.
- [ ] Intentar abrir sin FFmpeg y comprobar que MP3 da diagnóstico útil.
- [ ] Generar `.exe` usando BUILD_EXE_WINDOWS.cmd y ejecutarlo en equipo Windows limpio con yt-dlp dentro del EXE.
- [ ] Revisar antivirus/SmartScreen, SHA-256 y firmas antes de distribución.

**No marques la beta como estable sin comprobar estas pruebas en una instalación real de Windows.**
