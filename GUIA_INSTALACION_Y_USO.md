# Guía de instalación, uso y requisitos — Apex Descarga

**Producto del ecosistema Apex Software Inc.** (denominación de marca utilizada por este proyecto; no implica certificación ni acredita por sí sola una sociedad legalmente constituida).

## Para qué sirve
Gestionar descargas de vídeo MP4 y audio MP3 de contenido propio o autorizado: análisis de enlace, miniatura, calidades, cola, historial y selección de carpeta.

## Descargas disponibles
[Android 1.0.1 Preview (APK DEBUG)](https://github.com/Sombra-789/apex-descarga/releases/tag/android-v1.0.1-preview) · [Brave/Windows 1.2.3 (ZIP de actualización)](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3)

**Importante:** GitHub Actions Artifacts puede exigir inicio de sesión y caducar. Los paquetes beta/preview no se equiparan a versiones estables.

## Instalación paso a paso
**Android:** Android 10 (API 29) o posterior y ARM64; descarga el APK Preview, verifica su origen/huella, abre el archivo y autoriza únicamente la instalación puntual desde esa fuente. Preview usa identificación propia para no sobrescribir RC1. **Brave:** necesitas una instalación previa funcional de la extensión y host nativo; descarga el ZIP 1.2.3, extrae, cierra Brave, ejecuta `brave-windows/ACTUALIZAR_APEX.cmd`, elige la carpeta original de extensión y recarga en `brave://extensions`. Si Native Messaging indica acceso prohibido, utiliza `REPARAR_APEX.cmd` con confirmación y respaldo. **No es instalador desde cero.**

## Cómo funciona y cómo utilizarlo
Pega o analiza un enlace permitido, comprueba los metadatos, elige MP4 o MP3 y calidad disponible, configura la carpeta y ejecuta. Supervisa la cola, cancela o revisa el historial. En Android también puedes configurar la política de red y consultar la biblioteca.

## Requisitos y dependencias
Android: Android >=10, ARM64 (emulador x86_64), almacenamiento e internet; APK DEBUG sin firma de producción. Compilar: JDK 17/21, SDK 35, Gradle y dependencias de `android/app/build.gradle` (youtubedl-android library/ffmpeg 0.18.1). Brave: Windows 11 probado, Brave/Chromium compatible con Manifest V3, Python y host local Native Messaging, yt-dlp y FFmpeg configurados; el ZIP de actualización NO incluye host compilado. Las dependencias externas deben conservar sus respectivas licencias.

## Limitaciones, seguridad y privacidad
Los sitios pueden cambiar o bloquear extracciones; no evita DRM; requiere conectividad y espacio. MP3/mezcla pueden depender de FFmpeg. El APK Android es de pruebas; firmas diferentes impiden actualización directa. Los enlaces y metadatos se consultan en servicios externos; no prometer privacidad absoluta. La edición Desktop independiente se retiró por decisión del propietario el 28-10-2026; no se soporta ni se recomienda descargarla.

## Más información
- [Repositorio GitHub](https://github.com/Sombra-789/apex-descarga)
- [Ficha de proyecto en Notion](https://app.notion.com/p/3fb252e21ba6810790aedb0298bd09f2)
- Consulta el README y las notas de cada versión para instrucciones adicionales.

---
© 2026 Apex Software Inc. — Identidad de proyecto. Las bibliotecas externas pertenecen a sus respectivos titulares y conservan sus licencias. No se afirma registro mercantil ni afiliación con terceros.
