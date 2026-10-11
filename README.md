# APEX DESCARGA — Android + Brave/Windows 11

**Estado: 1.0.0-rc1 — candidato de lanzamiento, no publicación estable firmada.**

Proyecto de **Apex Visual Studio** para gestionar descargas de medios **propios o autorizados**. Contiene dos productos relacionados con bases de código distintas:

| Producto | Ruta | Versión del código incluido |
|---|---|---|
| Aplicación nativa Android | [`android/`](android/) | **1.0.0-rc1** basada en la 0.6 verificada manualmente |
| Extensión Brave/Chromium + host local Windows | [`brave-windows/`](brave-windows/) | **1.2.2** (última actualización aportada por el propietario) |

> Android utiliza su propia numeración 1.0.0-rc1; la extensión Brave conserva su numeración independiente **1.2.2**. El paquete Brave 1.2.2 es una actualización sobre una instalación previa y no garantiza instalación completamente nueva sin registrar Native Messaging.

## Qué hace

### Android
- Descarga MP4/MP3 con motor `yt-dlp` por medio de una biblioteca Android; usa FFmpeg cuando corresponde.
- Vista previa con título, autor, duración, miniaturas y formatos cuando los facilita el sitio.
- Cola secuencial, notificaciones, historial/biblioteca, compartir enlaces a Apex, apertura/compartición de archivos.
- Paletas personalizables y colores HEX, logotipo opcional, modo solo Wi-Fi, comprobaciones de almacenamiento y actualización programada de motor.
- Diseño nativo inspirado en [Apex UI Pro (Figma)](https://www.figma.com/design/tnVTpd2xcdL4XqrEuWmNUH).

### Brave + Windows
- Popup Manifest V3 y Native Messaging con host Python.
- Detección de enlace en pestaña activa autorizada, vista previa, selector de calidad, MP4/MP3, transportes alternativos cuando los ofrece yt-dlp.
- Cola secuencial, cancelación, historial local, selector nativo de carpeta Windows y persistencia de la ruta en `settings.json`.
- Solicitud de aceptación de las condiciones revisadas en 1.2.2, con política de privacidad local y avisos sobre contenido de terceros.
- Depende de Python, yt-dlp, FFmpeg y del entorno JS compatible (por ejemplo Deno para ciertos sitios).

## Compilación Android (Windows 11)

1. Instala **Android Studio + SDK Platform 35** y **JDK 17 o 21**.
2. En la carpeta `android/`, ejecuta `GENERAR_APK_WINDOWS.cmd` sin privilegios de administrador.
3. La salida será `android/APEX_DESCARGA_ANDROID_1.0_RC1_DEBUG.apk`, **solo para pruebas**.
4. Para un APK público, audita dependencias, cambia la configuración de release cuando sea necesario y **firma con una clave privada que nunca se sube al repositorio**. Consulta [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

**Atención:** Si tu instalación previa se firmó con una clave *debug* diferente, Android rechazará la actualización. Antes de desinstalar, considera que pueden perderse datos y ajustes.

## Instalación Brave

Lee [`brave-windows/README_PRIMERO.md`](brave-windows/README_PRIMERO.md): registra el componente local y carga la carpeta `extension/` desde Brave Developer Mode. Esta fuente corresponde a la **actualización 1.2.2** facilitada por el propietario, no a una publicación de tienda. Requiere configuración previa del componente local y Native Messaging.

## Versión Brave 1.2.2: novedades

- Cambio de carpeta de destino mediante selector de Windows.
- Ruta persistente en `%LOCALAPPDATA%\ApexVideoDownloader\settings.json`.
- Avisos de privacidad y términos revisados, aceptados una vez por versión de condiciones.
- Actualizador de Windows conserva el ID de extensión al actualizar la carpeta original y realiza copia de seguridad.
- La extensión mantiene los permisos `activeTab`, `nativeMessaging` y `storage` y no incorpora telemetría propia. **yt-dlp y miniaturas sí se comunican con sitios externos**.

## Seguridad, privacidad y licencias

- Únicamente enlaces HTTP(S) que el usuario solicita; la extensión usa permisos `activeTab`, `nativeMessaging` y `storage`.
- No estamos afiliados a YouTube, TikTok, Instagram, Meta, Google, Brave ni sus propietarios.
- No hay garantías de que una plataforma ofrezca un formato, permita descargas o sea accesible sin sesión; no se evade DRM.
- El código puede incluir bibliotecas y herramientas de terceros con obligaciones de licencia diferentes. Lee [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) y [`PRIVACY.md`](PRIVACY.md).
- Licencia del **código de este repositorio**: GPL-3.0, sujeto a que el autor tenga derechos para licenciar cada parte. El logotipo/marca no se concede bajo GPL para uso comercial o suplantación; ver [`BRANDING.md`](BRANDING.md).

## Estado de validación

Las versiones Android previas hasta 0.6 fueron probadas manualmente por el creador en Galaxy S23, con descargas correctas en varias plataformas. **Esta compilación candidata 1.0 no ha sido firmada ni verificada en dispositivo o Android SDK dentro de este entorno**. El pipeline de Actions intenta construir un APK de depuración para pruebas, no un lanzamiento de producción.

## Documentación

- [Registro de cambios](CHANGELOG.md)
- [Guía de publicación](RELEASE_CHECKLIST.md)
- [Avisos de terceros](THIRD_PARTY_NOTICES.md)
- [Privacidad](PRIVACY.md)
- [Política de seguridad](SECURITY.md)
- [Créditos y marca](BRANDING.md)
- [Android: README](android/README_PRIMERO.md)
- [Brave: README](brave-windows/README_PRIMERO.md)
- [Brave 1.2.2: cambios](brave-windows/CAMBIOS_1.2.2.md)
- [Brave 1.2.2: privacidad y condiciones](brave-windows/PRIVACIDAD_Y_CONDICIONES.md)

## Sobre la autoría

Iniciativa y decisiones de producto, diseño y pruebas de **Apex Visual Studio**, con asistencia de inteligencia artificial para generación de código, depuración y redacción; las pruebas manuales y decisiones de lanzamiento pertenecen al responsable del proyecto.