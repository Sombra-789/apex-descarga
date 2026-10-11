# Cambios de Apex 1.2

- **Novedad:** Vista previa a demanda: título, miniatura, duración, canal y resoluciones detectadas.
- **Novedad:** Cola de 15 descargas pendientes, ejecuciones secuenciales, quitar y reanudar.
- **Novedad:** Cancelación de la descarga activa a través de Native Messaging y terminación del proceso yt-dlp; pueden persistir archivos `.part`.
- **Novedad:** Abrir carpeta de descargas desde el panel.
- **Novedad:** Historial ampliado a 30 entradas y preferencias de formato conservadas.
- **Mejora:** Detección de enlaces específicos en pestaña activa; no rellenar automáticamente enlaces de ChatGPT u otros sitios ajenos.
- **Mejora:** Opciones de H.264/AAC, transporte HLS y mensajes amigables según el error.
- **Seguridad:** Sin permisos extra, ejecución sin shell, validación de URL y mensajes nativos limitados.
- **Actualización:** Conservar la carpeta `extension` original, EXE y registro; crea respaldo antes de copiar.
- **Limitación:** La vista previa no está disponible para todos los sitios, el método alternativo no garantiza solucionar un HTTP 403 y no se descarga contenido con DRM.
