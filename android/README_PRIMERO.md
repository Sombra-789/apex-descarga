# Apex Descarga Android 1.0.1 — Actualización de mantenimiento (beta)

**Implementación nativa del diseño Figma:** https://www.figma.com/design/tnVTpd2xcdL4XqrEuWmNUH

Esta actualización aplica un rediseño Android a la base **funcional 0.5**, sin modificar las operaciones de yt-dlp/FFmpeg ni las claves de datos. Los archivos son un **proyecto de código fuente**, no un APK ya compilado.

## Generar la APK en Windows 11

1. Descomprime el ZIP por completo y abre la carpeta `android`.
2. Ejecuta `GENERAR_APK_WINDOWS.cmd` (no como administrador).
3. Utiliza Android SDK 35, JDK 17/21 y conexión a internet para Gradle. Si tienes Android Studio, basta con dejar configurado el SDK.
4. Cuando aparezca `BUILD SUCCESSFUL`, encontrarás `APEX_DESCARGA_ANDROID_1.0.1_DEBUG.apk` en la raíz del proyecto.
5. Crea una copia de seguridad de datos importantes antes de actualizar. Instálala encima de 0.5 **sin desinstalar**, siempre que la firma de depuración sea la misma.
6. Si Android indica **firma incompatible**, no desinstales automáticamente: eso borraría datos privados, cola e historial.

## Pantallas rediseñadas

- **Inicio:** portada visible, enlace, selector MP4/MP3, calidad y botón principal. Tarjeta de estado de la cola.
- **Cola:** gestor con tarjetas, filtros, progreso, cancelación, reintento y abrir archivos.
- **Biblioteca:** búsqueda, miniaturas, abrir/compartir/eliminar.
- **Ajustes:** paletas, HEX personalizado, logo opcional, solo Wi-Fi, carpeta destino y actualización de yt-dlp.
- **Conversor:** mantiene extracción M4A y recorte MP4 y ahora comparte navegación.

## Lo que NO cambia

Mismo applicationId `com.apexvisualstudio.descarga`, mismas preferencias (`apex_descarga`), servicio de descargas, cola, biblioteca, red y actualización de yt-dlp de la 0.5.

## Comprobaciones y limitaciones

El código se verificó mediante análisis de sintaxis Java, verificaciones estructurales y pruebas Java del proyecto. **Este entorno no cuenta con Android SDK ni acceso a los paquetes de compilación**, de modo que la APK y su comportamiento deben verificarse aún en Windows/Android. No publiques un `debug.apk` como aplicación final: necesita revisión y firma de lanzamiento.

El icono y logotipo son los assets originales del proyecto; las pantallas Figma son una guía visual editable, no una dependencia del APK.

Ver `CAMBIOS_0.6.md` y `PRUEBAS_GALAXY_S23.md`.


> Revisión 1.0-rc1: cambia versión y añade documentación de distribución; los motores de descarga siguen los de 0.6. No distribuir la APK debug como release. Consulta ../RELEASE_CHECKLIST.md.

## Android 1.0.1

Corrección de la interpretación de las versiones de yt-dlp, mensajes claros ante actualizaciones no verificadas, y presentación dinámica de errores en Ajustes. Las descargas MP4/MP3, archivos existentes, historial y preferencias no se han cambiado. GitHub genera un APK DEBUG para pruebas; puede no actualizar una versión anterior con firma diferente. No borres los datos sin crear antes una copia de seguridad.
