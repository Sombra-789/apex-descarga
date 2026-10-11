# APEX DESCARGA — Android + Brave/Windows 11

**Estado: 1.0.0-rc1 — versión de pruebas (APK debug), todavía no versión estable de producción.**

Proyecto de **Apex Visual Studio** para gestionar descargas de medios **propios o autorizados**. Contiene tres productos relacionados con bases de código distintas:

| Producto | Ruta | Versión del código incluido |
|---|---|---|
| Aplicación nativa Android | [`android/`](android/) | **1.0.0-rc1** basada en la 0.6 verificada manualmente |
| Extensión Brave/Chromium + host local Windows | [`brave-windows/`](brave-windows/) | **1.2.2** (última actualización aportada por el propietario) |
| Aplicación independiente Windows 11 | [`desktop-windows/`](desktop-windows/) | **0.2.0 UI Pro** (beta de escritorio) |
| **Aplicación independiente Windows 11** | [`desktop-windows/`](desktop-windows/) | **Beta 0.1.0** (EXE en validación) |

> Android utiliza su propia numeración 1.0.0-rc1; la extensión Brave conserva su numeración independiente **1.2.2**. El paquete Brave 1.2.2 es una actualización sobre una instalación previa y no garantiza instalación completamente nueva sin registrar Native Messaging.

## Qué hace

### Android
- Descarga MP4/MP3 con motor `yt-dlp` por medio de una biblioteca Android; usa FFmpeg cuando corresponde.
- Vista previa con título, autor, duración, miniaturas y formatos cuando los facilita el sitio.
- Cola secuencial, notificaciones, historial/biblioteca, compartir enlaces a Apex, apertura/compartición de archivos.
- Paletas personalizables y colores HEX, logotipo opcional, modo solo Wi-Fi, comprobaciones de almacenamiento y actualización programada de motor.
- Diseño nativo inspirado en [Apex UI Pro (Figma)](https://www.figma.com/design/tnVTpd2xcdL4XqrEuWmNUH).

### Desktop — Windows 11
- Aplicación independiente de Brave y Android con interfaz oscura Apex, temas HEX, Inicio/Cola/Biblioteca/Ajustes.
- Descargas MP4 y MP3 con yt-dlp incorporable al ejecutable, FFmpeg/Deno externos cuando sean necesarios.
- Cola secuencial, vista previa y portadas, progreso y cancelación/reintento, carpeta de destino configurable e historial local.
- **Beta 0.1.0**: 22 pruebas unitarias aprobadas. El ejecutable PyInstaller está en proceso de validación mediante [GitHub Actions](https://github.com/Sombra-789/apex-descarga/actions/workflows/desktop-windows.yml); todavía **no es una versión Windows firmada ni estable**.
- Ejecutar el código con `desktop-windows/INICIAR_APEX.cmd` o compilar usando `desktop-windows/BUILD_EXE_WINDOWS.cmd`. [Manual de Desktop](desktop-windows/README.md). 

### Windows 11 — aplicación independiente

- **Apex Descarga Desktop 0.2 UI Pro** funciona sin tener Brave abierto: navegación de cinco pantallas, cola, miniaturas, biblioteca, filtros, ajustes de apariencia y pantalla Acerca de.
- Descarga MP4/MP3 mediante yt-dlp, y requiere FFmpeg instalado para MP3 y para unir pistas de video HD cuando sea necesario.
- Código: [desktop-windows/](desktop-windows/) · [Guía de inicio](desktop-windows/README.md) · [Capturas](desktop-windows/docs/UI_PRO_VISTA_GENERAL.jpg).
- [Descargar beta Windows](https://github.com/Sombra-789/apex-descarga/releases/tag/desktop-v0.2.0-beta) cuando GitHub Actions haya terminado; archivo `ApexDescargaDesktop.exe` **sin firma Authenticode**, para pruebas exclusivamente.

### Brave + Windows
- Popup Manifest V3 y Native Messaging con host Python.
- Detección de enlace en pestaña activa autorizada, vista previa, selector de calidad, MP4/MP3, transportes alternativos cuando los ofrece yt-dlp.
- Cola secuencial, cancelación, historial local, selector nativo de carpeta Windows y persistencia de la ruta en `settings.json`.
- Solicitud de aceptación de las condiciones revisadas en 1.2.2, con política de privacidad local y avisos sobre contenido de terceros.
- Depende de Python, yt-dlp, FFmpeg y del entorno JS compatible (por ejemplo Deno para ciertos sitios).

## 📦 Descargar APK de pruebas (Android 1.0 RC1)

Busca la **pre-release** [Apex Descarga 1.0 RC1 — APK de prueba](https://github.com/Sombra-789/apex-descarga/releases/tag/v1.0.0-rc1) cuando haya terminado su compilación/publicación. Descarga el archivo `Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk` y verifica el SHA-256 publicado junto a él.

> ⚠️ El APK está firmado con **certificado de depuración de CI**, no con una clave release de Apex Visual Studio. Es una distribución para pruebas técnicas; puede requerir un dispositivo o perfil sin otra versión instalada con una firma diferente. No desinstales versiones anteriores con datos importantes solo por solucionar un conflicto de firma. No incluye garantía de compatibilidad para todos los sitios o dispositivos.

**Contacto para reportar fallos o sugerencias:** [angelrlpz030207@gmail.com](mailto:angelrlpz030207@gmail.com). Incluye modelo, versión de Android/Windows, pasos para reproducir y mensaje de error, **sin enviar contraseñas, cookies, tokens, enlaces privados ni información sensible**. También puedes abrir una [incidencia en GitHub](https://github.com/Sombra-789/apex-descarga/issues) cuando el repositorio esté accesible.

## Compilación Android (Windows 11)

1. Instala **Android Studio + SDK Platform 35** y **JDK 17 o 21**.
2. En la carpeta `android/`, ejecuta `GENERAR_APK_WINDOWS.cmd` sin privilegios de administrador.
3. La salida será `android/APEX_DESCARGA_ANDROID_1.0_RC1_DEBUG.apk`, **solo para pruebas**.
4. Para un APK público, audita dependencias, cambia la configuración de release cuando sea necesario y **firma con una clave privada que nunca se sube al repositorio**. Consulta [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

**Atención:** Si tu instalación previa se firmó con una clave *debug* diferente, Android rechazará la actualización. Antes de desinstalar, considera que pueden perderse datos y ajustes.

## Instalación Brave

Lee [`brave-windows/README_PRIMERO.md`](brave-windows/README_PRIMERO.md): registra el componente local y carga la carpeta `extension/` desde Brave Developer Mode. Esta fuente corresponde a la **actualización 1.2.2** facilitada por el propietario, no a una publicación de tienda. Requiere configuración previa del componente local y Native Messaging.

## Versión Desktop 0.2 UI Pro

- Diseño visual profesional basado en el estilo Apex, funciones originales preservadas y datos locales compatibles con Desktop 0.1.
- Requiere Windows 11; el `.exe` empaqueta Python/yt-dlp pero **no FFmpeg ni Deno**.
- Errores y sugerencias: **angelrlpz030207@gmail.com**.

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

La compilación automatizada **1.0 RC1** con Gradle y SDK 35 se completó con éxito en GitHub Actions; Brave superó las pruebas automatizadas Python/JavaScript. El creador confirmó en **Galaxy S23** la actualización de 0.6 a 1.0 RC1 conservando datos, descargas MP4 y MP3 y pruebas básicas de cola, segundo plano, Solo Wi-Fi, interrupción de red, cancelación y reintento. También confirmó el funcionamiento de **Brave 1.2.2 en Windows 11**. Detalles: [seguimiento de validación #1](https://github.com/Sombra-789/apex-descarga/issues/1).

**El APK descargable es de DEPURACIÓN (DEBUG), para pruebas exclusivamente.** Es posible que no se pueda actualizar una instalación firmada con otra clave sin perder los datos de la app. No usar como APK estable ni publicarlo en tiendas. Sigue pendiente probarlo en otros modelos Android, comprobar las licencias de FFmpeg y generar una versión release firmada.

## Documentación

- [Registro de cambios](CHANGELOG.md)
- [Guía de publicación](RELEASE_CHECKLIST.md)
- [Avisos de terceros](THIRD_PARTY_NOTICES.md)
- [Privacidad](PRIVACY.md)
- [Política de seguridad](SECURITY.md)
- [Créditos y marca](BRANDING.md)
- [Android: README](android/README_PRIMERO.md)
- [Brave: README](brave-windows/README_PRIMERO.md)
- [Desktop 0.2: README](desktop-windows/README.md)
- [Desktop 0.2: historial de cambios](desktop-windows/CHANGELOG.md)
- [Brave 1.2.2: cambios](brave-windows/CAMBIOS_1.2.2.md)
- [Brave 1.2.2: privacidad y condiciones](brave-windows/PRIVACIDAD_Y_CONDICIONES.md)

## Contacto y colaboración

Correo del proyecto: **angelrlpz030207@gmail.com**. Se aceptan avisos de errores, reportes reproducibles y sugerencias de mejora.

## Sobre la autoría

Iniciativa y decisiones de producto, diseño y pruebas de **Apex Visual Studio**, con asistencia de inteligencia artificial para generación de código, depuración y redacción; las pruebas manuales y decisiones de lanzamiento pertenecen al responsable del proyecto.
