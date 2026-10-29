# 🦅 Apex Descarga — Apex Software Inc.

> **Apex Software Inc. — Proyecto del ecosistema Apex Software.** [Guía completa de instalación, funcionamiento, requisitos, dependencias y limitaciones](GUIA_INSTALACION_Y_USO.md). La denominación “Inc.” se usa como identidad de proyecto y no constituye prueba de registro legal.

## 📱 DESCARGAR APEX DESCARGA PARA ANDROID

### ⬇️ [**DESCARGAR APK 1.0.1 PREVIEW **](https://github.com/Sombra-789/apex-descarga/releases/download/android-v1.0.1-preview/Apex-Descarga-Android-1.0.1-PREVIEW-TESTING.apk)

**Nuevo:** mantenimiento del actualizador de yt-dlp. Se instala como aplicación de pruebas **separada** para no sobrescribir ni borrar datos de la 1.0 RC1 existente. La descarga estará disponible cuando GitHub Actions termine su publicación. [Ver cambios 1.0.1](docs/ANDROID_1_0_1.md).

### ⬇️ [**DESCARGAR APK ANTERIOR — ANDROID 1.0 RC1**](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk)

**Descarga directa, sin abrir carpetas ni entrar a GitHub Actions.** Abre este README desde el teléfono y toca el enlace de arriba. GitHub descargará el archivo `Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk` (aprox. 115 MB).

> **Versión Android 1.0 RC1 de pruebas (DEBUG).** Compatible con Android 10 o superior en ARM64. No equivale a la versión 1.2.3 de Brave/Windows y no se debe presentar como una aplicación Android estable. Si Android señala una firma distinta a una instalación previa, no desinstales sin respaldar tus datos.

[Ver detalles de la versión Android](https://github.com/Sombra-789/apex-descarga/releases/tag/v1.0.0-rc1) · [Comprobar SHA-256](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk.sha256)

---

**Estado del proyecto: desarrollo principal finalizado. Mantenimiento y actualizaciones menores únicamente.**

Apex Descarga permite gestionar descargas de contenido **propio o autorizado**. Este repositorio conserva **dos ediciones activas: Brave/Windows y Android**, con versiones y estados de publicación distintos. La aplicación Windows Desktop independiente ha sido retirada por decisión del propietario.

## 📦 Descargas oficiales de GitHub

| Plataforma | Versión | Estado | Descarga |
| --- | --- | --- | --- |
| **Brave + Windows** | **1.2.3** | **Estable para instalaciones existentes** | [ZIP de actualización 1.2.3](https://github.com/Sombra-789/apex-descarga/releases/download/brave-v1.2.3/Apex-Descarga-Brave-1.2.3-Actualizacion.zip) |
| **Android** | **1.0.1 Preview** | **APK de pruebas independiente** | **[Descargar APK 1.0.1](https://github.com/Sombra-789/apex-descarga/releases/download/android-v1.0.1-preview/Apex-Descarga-Android-1.0.1-PREVIEW-TESTING.apk)** |

**Página de todas las publicaciones:** [GitHub Releases](https://github.com/Sombra-789/apex-descarga/releases).

### 📱 Instalar el APK Android

El APK Android ya está publicado en la [versión de pruebas 1.0 RC1](https://github.com/Sombra-789/apex-descarga/releases/tag/v1.0.0-rc1). Puedes descargarlo directamente desde el enlace de arriba.

1. Descarga el archivo **Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk** en tu teléfono Android compatible.
2. Para comprobar la integridad descarga también su [archivo SHA-256](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk.sha256).
3. Abre el APK desde tu gestor de archivos y, solo si confías en el origen, concede autorización puntual para instalar desde esa fuente.
4. Prueba la aplicación con contenido autorizado.

**Advertencia:** el APK de 1.0 RC1 está firmado con un **certificado DEBUG de GitHub Actions**, no con una clave de distribución estable. Está destinado a pruebas; Android puede impedir actualizar encima de otra copia firmada con una clave distinta. **No desinstales una versión que contenga datos importantes** para resolver un error de firma. La compatibilidad declarada es Android 10 o posterior, con arquitectura ARM de 64 bits (o emulador x86_64). La versión estable **1.2.3 corresponde a Brave + Windows, NO a Android**.

### 🖥️ Brave + Windows — 1.2.3 estable

La versión 1.2.3 de Brave + Windows fue verificada manualmente con descargas MP4/MP3, vista previa, carpetas, cola/historial y conexión Native Messaging. El reparador **REPARAR_APEX.cmd** corrigió un error de permisos del host cuando cambió el ID de la extensión. También se aprobaron las pruebas automáticas de diagnóstico y empaquetado.

**El ZIP de 1.2.3 es solo una actualización:** no contiene un instalador completo ni un host ejecutable compilado. Requiere tener Apex previamente instalado y configurado con Python, yt-dlp y las dependencias pertinentes.

1. Extrae el ZIP completo, cierra Brave y ejecuta **ACTUALIZAR_APEX.cmd**, sin privilegios de administrador.
2. Selecciona la carpeta **original** de la extensión que ya está cargada en Brave; no la carpeta nueva del ZIP.
3. Recarga la extensión en **brave://extensions** y confirma **1.2.3** y **Conectado**.
4. Si aparece un error de permiso Native Messaging, ejecuta **REPARAR_APEX.cmd** y sigue las instrucciones para autorizar el ID de Brave. La herramienta solicita confirmación y crea un respaldo.

[Manual Brave/Windows](brave-windows/README_PRIMERO.md) · [Cambios de 1.2.3](brave-windows/CAMBIOS_1.2.3.md) · [Historial](CHANGELOG.md)

## Funcionalidades y código fuente

| Producto | Código | Capacidades principales |
| --- | --- | --- |
| **Brave/Windows 1.2.3** | [brave-windows/](brave-windows/) | Pestaña activa, vista previa, MP4/MP3, calidades, cola e historial, cambiar/abrir carpeta, reparador Native Messaging |
| **Android 1.0 RC1** | [android/](android/) | Descargas MP4/MP3, vista previa, cola, biblioteca, notificaciones, selección de tema y control de red |
| **Prototipo 2.0** | [prototypes/apex-descarga-2.0 (rama experimental)](https://github.com/Sombra-789/apex-descarga/tree/feature/apex-descarga-2.0-alpha1/prototypes/apex-descarga-2.0) | Interfaz interactiva local **simulada**, separada de producción y conservada como referencia futura |

**El prototipo 2.0 no es una actualización disponible de 1.2.3 ni realiza descargas reales.** Permanece únicamente como referencia experimental en una rama separada.

## Mantenimiento

- **Versión estable elegida para Brave:** 1.2.3.
- El desarrollo principal se da por concluido; solo se prevén correcciones, mantenimiento de seguridad y mejoras menores cuando sean necesarias.
- Android 1.0.1 sigue siendo una versión Preview de pruebas, no un producto estable. La edición Desktop independiente se retiró.
- No se recopila telemetría hacia servidores propios de Apex; las descargas o previsualizaciones **sí requieren contactar** con los sitios externos.
- No se ofrece evasión de DRM ni garantía de compatibilidad con todos los portales.
- Antes de instalar archivos descargados, verifícalos y revisa el código abierto.

## Documentación y contacto

[Política de privacidad](PRIVACY.md) · [Seguridad](SECURITY.md) · [Licencias de terceros](THIRD_PARTY_NOTICES.md) · [Checklist de publicación](RELEASE_CHECKLIST.md) · [Seguimiento Android](docs/RC1-TESTING-RELEASE.md) · [Cierre y mantenimiento](docs/CIERRE_PROYECTO.md).

Para fallos o sugerencias, abre una [incidencia en GitHub](https://github.com/Sombra-789/apex-descarga/issues). No compartas contraseñas, cookies, enlaces privados ni archivos sensibles.

**Apex Descarga forma parte de Apex Software Inc.**, con apoyo de herramientas de inteligencia artificial en el desarrollo. La marca y los logotipos se rigen por [BRANDING.md](BRANDING.md); el código se distribuye según [LICENSE](LICENSE) y las licencias de sus dependencias.
