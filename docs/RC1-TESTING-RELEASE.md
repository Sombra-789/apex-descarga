# Apex Descarga Android 1.0.0-rc1 — APK de pruebas

**Candidata de lanzamiento para evaluación pública o privada; NO es la versión 1.0 estable.**

Este APK se genera automáticamente desde el código abierto del proyecto mediante GitHub Actions y Gradle. Está **firmado con una clave de depuración temporal del entorno de compilación**, y por lo tanto **NO debe distribuirse como una release de producción ni publicarse en Google Play**.

## Compatibilidad y funcionalidades

- Android 10 o posterior, procesadores `arm64-v8a` (dispositivos Android de 64 bits) y `x86_64` (emuladores compatibles).
- Descargas MP4/MP3 de contenido propio o autorizado; disponibilidad según cada proveedor.
- Cola y progreso, notificaciones, biblioteca con portadas, controles de datos móviles y Wi-Fi, temas HEX y logotipo opcional.
- Compartir enlaces desde otras aplicaciones, motor yt-dlp actualizable y conversor local experimental.

## Cómo descargar y probar

1. En **Assets** descarga `Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk` y el archivo `.sha256`.
2. Comprueba el SHA-256 del APK, por ejemplo con `Get-FileHash -Algorithm SHA256` desde PowerShell en Windows.
3. Instálalo únicamente si confías en el proyecto y tienes un equipo/perfil para pruebas; Android puede pedir autorización para instalar APK de esta fuente.
4. **IMPORTANTE:** el APK lleva una firma de depuración distinta de la utilizada por otras compilaciones. Si Android informa «App no instalada»/firma incompatible al actualizar una versión anterior, **no desinstales la que ya tienes ni pierdas sus datos**. Usa otro dispositivo/perfil o compila con tu certificado de desarrollo anterior.
5. Prueba las funciones sin introducir enlaces privados, contraseñas, cookies ni información sensible en tus reportes. Notifica los problemas reproducibles.

## Contacto para fallos y sugerencias

**angelrlpz030207@gmail.com** — incluye modelo, versión Android, pasos para reproducir y mensaje de error. Evita enviar credenciales o archivos personales.

También puedes consultar [GitHub Issues](https://github.com/Sombra-789/apex-descarga/issues) cuando el repositorio sea accesible al público.

## Limitaciones y avisos

- Una pre-release no ha sido validada en todos los dispositivos. Algunas plataformas cambian frecuentemente y las descargas pueden fallar.
- Respeta los derechos de autor y los términos de cada servicio; no usar para evadir DRM.
- **Pendiente**: auditoría de licencias de FFmpeg y bibliotecas empaquetadas, prueba en múltiples teléfonos y firma **release** propia, verificada con `apksigner`.
- La fuente está en [android/](https://github.com/Sombra-789/apex-descarga/tree/main/android) y las condiciones del proyecto en [THIRD_PARTY_NOTICES.md](https://github.com/Sombra-789/apex-descarga/blob/main/THIRD_PARTY_NOTICES.md).

**Brave/Windows 1.2.3 estable** también tiene código fuente en este repositorio. El APK 1.0.0-rc1 es una **compilación independiente para Android y solo de pruebas**, no una versión 1.2.3 de Android.
