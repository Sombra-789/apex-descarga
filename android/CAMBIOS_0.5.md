# Apex Descarga Android 0.5.0 — cierre de funciones

**Apex Visual Studio** · Proyecto fuente para Android · Beta previa a estabilización 1.0.

Esta versión **continúa 0.4**, con el mismo `applicationId`, mismas dependencias probadas y claves locales para configuración, cola y biblioteca. No está compilada ni validada en un teléfono por el entorno de desarrollo que generó este paquete.

## Nuevas funciones

### Compartir enlaces a Apex

- Continúa el filtro `ACTION_SEND` para enlaces compartidos desde otras aplicaciones Android, sin permiso para leer otras apps.
- Ahora, tras recibir el enlace, intenta **analizarlo automáticamente** al inicializarse el motor, mostrando vista previa y portada cuando la plataforma la proporciona.
- Solo recibe URLs HTTP(S); no agrega ni descarga sin la aprobación del usuario y la aceptación de las condiciones.

### Wi-Fi, consumo y espacio

- Opción **Solo Wi-Fi**. Impide iniciar nuevos trabajos en datos móviles; si pierde Wi-Fi durante la transferencia, intenta detener el proceso y marca el trabajo `Pausado` para retomarlo manualmente.
- Opción de **advertencia por tamaño estimado**: 50, 100, 250 o 500 MB. Si estás en una red medida y la estimación supera el umbral, o no existe estimación, solicita confirmación.
- Comprueba el espacio temporal disponible antes de iniciar; conserva margen para fragmentos multimedia y combinación de audio/video.
- `Reanudar pendientes` y `Reintentar` **vuelven a ejecutar el trabajo**; no se implementa aún una reanudación garantizada byte por byte del archivo parcial.

### MP3: artista, título y carátula

- Usa `yt-dlp --embed-metadata`, `--write-thumbnail`, `--convert-thumbnails jpg` y `--embed-thumbnail` antes de publicar el MP3.
- Si la incorporación de metadatos/portada falla, prueba otra vez en una carpeta limpia descargando MP3 sin enriquecimiento. Esto evita perder descargas por problemas de postprocesamiento; **no garantiza** la portada en todos los proveedores.
- Si la plataforma proporciona metadata incorrecta, la etiqueta resultante también puede ser incorrecta. La biblioteca continúa guardando título, autor y miniatura para uso dentro de Apex.

### Actualización estable de yt-dlp

- Conserva comprobación aproximadamente semanal cuando Android permite la ejecución, con red no medida y batería suficiente.
- Comprueba la **versión resultante** y registra `engine_previous_version`, `engine_version_last`, la fecha y errores del intento.
- No ejecuta una actualización automática si detecta una descarga activa.
- El botón manual solicita confirmación cuando la red es de pago/medida.
- **Alcance de verificación:** usa el actualizador estable que proporciona `youtubedl-android` y valida su cadena de versión. No ofrece verificación criptográfica independiente ni restauración automática del ejecutable anterior. Esto seguirá como tarea de seguridad para la versión estable.

### Rendimiento y estabilidad

- Caché de carátulas limitada a aproximadamente 40 MB o 100 archivos, además de la caché de memoria existente.
- Corrige la condición que podía volver a iniciar la cola repetidamente cuando se activaba Solo Wi-Fi sin conexión.
- Restablece solo trabajos `waiting` al regresar a la app y si la política de red lo permite; trabajos `paused` esperan acción manual.
- Conserva el servicio de notificaciones, cola de una descarga a la vez, portadas, biblioteca, búsqueda, convertidor M4A/recorte MP4, colores HEX y logotipo opcional sin borde.

## Archivos modificados

`MainActivity.java`, `DownloadService.java`, `EngineUpdateJob.java`, `MediaMetadata.java`, `DownloadQueueStore.java`, `ArtworkCache.java`, `PrivacyTerms.java`, `AndroidManifest.xml`, `app/build.gradle`, scripts y documentación.

**Nuevos:** `NetworkPolicy.java` y `EngineHealth.java`.

## Pendiente para 1.0

- Compilación Gradle real en Windows 11 con Android SDK 35.
- Pruebas en teléfonos de gama media, descargas largas, cambio de Wi-Fi a datos, memoria escasa y recuperación del proceso.
- Validación de metadatos ID3 y carátulas con las apps de música del teléfono.
- Firma de distribución, auditoría de privacidad/licencias y verificación criptográfica/rollback del motor.
- No incluye un conversor MP3 genérico de archivos locales: la descarga directa a MP3 sí está implementada.
