# Política técnica de privacidad (provisional para la versión candidata)

**Apex Descarga** no requiere crear una cuenta con Apex Visual Studio. En las versiones fuente examinadas, no se incluyeron anuncios, SDK de analítica propios ni un servidor central de telemetría de Apex Visual Studio. Esta declaración describe solo el código presente; debe verificarse antes de difundir un release público.

- **Almacenamiento local:** preferencias, historial/cola y referencias de archivos se guardan en el dispositivo o navegador según la versión. En Android, la aplicación tiene `allowBackup=false`.
- **Conexiones externas:** al analizar o descargar un enlace, el dispositivo se conecta a la plataforma de origen y puede revelar dirección IP, agente de usuario, URL y metadatos de la solicitud a esa plataforma. Las miniaturas pueden solicitarse a la misma plataforma. Las actualizaciones de yt-dlp se consultan desde repositorios externos de su proyecto.
- **Brave 1.2.2:** el selector de carpeta guarda la ruta elegida en `%LOCALAPPDATA%\ApexVideoDownloader\settings.json` en el equipo; la extensión guarda enlaces, cola/historial, preferencias y aceptación de condiciones en el almacenamiento local del navegador. Los términos locales actualizados requieren aceptación en la versión 1.2.2 antes de añadir descargas. Para detalles, consulta [`brave-windows/PRIVACIDAD_Y_CONDICIONES.md`](brave-windows/PRIVACIDAD_Y_CONDICIONES.md).
- **Brave Native Messaging:** los mensajes fluyen entre la extensión y el componente local; el host invoca yt-dlp sin pasar los enlaces por un servidor de Apex. La extensión declara `activeTab`, `nativeMessaging`, `storage`.
- **Android:** permisos para Internet, estado de red, servicio de primer plano y notificaciones; no se solicitaron permisos amplios de ubicación, acceso a toda la biblioteca multimedia ni credenciales de otros servicios.
- **Contenido y terceros:** solo descarga archivos autorizados. El comportamiento de cada web y motor externo puede cambiar. Los archivos pueden ser peligrosos: examínalos antes de abrirlos.
- **Datos y soporte:** antes de habilitar canales de reporte público, añade datos de contacto oficiales y explica cómo se recibirán y borrarán registros de errores, si los solicitas.

Esta política **no** garantiza que proveedores externos no traten datos. Requiere revisión final del responsable del proyecto antes de publicar.
