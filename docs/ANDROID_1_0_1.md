# Apex Descarga Android 1.0.1 Preview

Esta es una compilación **de pruebas**, con correcciones del actualizador yt-dlp observado en 1.0 RC1. **La versión Android fue probada en un Samsung Galaxy S23, pero no es exclusiva de ese teléfono.** Requiere Android 10+ y ARM64; aún deben validarse más modelos. No es una versión final ni una sustitución de la edición Brave/Windows 1.2.3.

## Cambios incluidos
- Normaliza versiones de yt-dlp aunque estén acompañadas por un prefijo, por ejemplo: "yt-dlp 2026.08.19".
- Distingue entre motor actualizado y verificado, versión sin cambios y actualización cuya versión no se pudo confirmar.
- Cuando falla el actualizador, muestra la causa real con un mensaje contextual, en vez de atribuir automáticamente el problema a una validación de versión.
- La sección de Ajustes actualiza inmediatamente el aviso sin tener que volver a entrar.
- Mantiene sin modificar descarga y conversión MP4/MP3, miniaturas, cola, biblioteca, selección de carpeta, preferencias y funcionamiento en segundo plano.

## Seguridad al instalar
El APK de esta publicación está compilado con una **firma DEBUG** de GitHub Actions. La versión anterior 1.0 RC1 fue compilada con otra firma DEBUG temporal, por lo que una actualización directa podría ser rechazada por Android.

Para **evitar perder los datos ya guardados**, esta compilación usa el identificador independiente `com.apexvisualstudio.descarga.preview`; se instala **al lado** de 1.0 RC1 y NO migra automáticamente su historial, sus archivos de aplicación ni sus ajustes.

No desinstales 1.0 RC1 ni borres sus datos. Confirma en el teléfono el nombre, versión y permiso de instalación antes de abrir el APK. Para futuras actualizaciones sobre la misma instalación hará falta una **clave release persistente y protegida**; no se ha configurado todavía.

## Qué comprobamos automáticamente
- Análisis estático del proyecto Android y pruebas del analizador de versiones en Java.
- Compilación de APK mediante Gradle y Android SDK 35.
- Comprobación de firma del APK, `applicationId` y versión, junto con SHA-256.
- Las pruebas de Brave + Windows se mantienen separadas y no modifican su versión estable.

## Pruebas manuales pendientes
En otros teléfonos Android compatibles, confirmar que el APK instala y abre, que el motor yt-dlp muestra la versión, que el actualizador diferencia resultados, y que MP4, MP3, miniaturas, cola, biblioteca, guardar/abrir/compartir y notificaciones siguen funcionando. Los tests estáticos no sustituyen pruebas en dispositivo.

## Descarga
APK directo: https://github.com/Sombra-789/apex-descarga/releases/download/android-v1.0.1-preview/Apex-Descarga-Android-1.0.1-PREVIEW-TESTING.apk

Ver versión y SHA-256: https://github.com/Sombra-789/apex-descarga/releases/tag/android-v1.0.1-preview

Esta versión solo está disponible después de que el flujo de publicación automática termine satisfactoriamente en main.
