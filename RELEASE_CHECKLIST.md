# Checklist de publicación — 1.0

**Estado inicial: PENDIENTE.** No etiquetar como estable ni subir `debug.apk` a Releases.

- [x] Compilar proyecto fuente usando GitHub Actions y Gradle/Android SDK 35 sin errores.
- [ ] Ejecutar pruebas estáticas, smoke tests Java y pruebas de extensión/host en Windows.
- [ ] Verificar Android en varios dispositivos y versiones compatibles (como mínimo Galaxy S23 y otro Android diferente).
- [ ] Comprobar actualizaciones sobre la instalación previa; las firmas deben coincidir. Guardar copia de seguridad antes de cualquier reinstalación.
- [ ] Probar YouTube, Shorts, TikTok, Instagram con contenido autorizado; comprobar audio/video, calidad real y «Mejor disponible».
- [ ] Probar pérdida de red, modo solo Wi-Fi, cambio Wi-Fi/datos, almacenamiento lleno, cancelación, 15 trabajos, segundo plano, metadatos y conversiones.
- [ ] Auditar FFmpeg y bibliotecas transitivas; completar licencias y avisos dentro del APK, entrega de código correspondiente y términos legales.
- [ ] Confirmar términos de uso y política de privacidad como textos públicos definitivos. Contacto disponible: angelrlpz030207@gmail.com.
- [ ] Generar APK release con clave privada administrada fuera de GitHub; comprobar firma con Android SDK apksigner.
- [ ] Registrar checksum SHA-256 del APK final y etiquetar commit/release estable solo cuando se cumplan los puntos anteriores.
- [x] Documentar la versión **Brave/Windows 1.2.2** y conservar su código fuente, actualizador y condiciones revisadas.
- [ ] Pruebas específicas Windows 11 de selector de carpeta, persistencia tras reinicio, aceptación de términos, copia de iconos y actualización sin cambiar el ID. El creador confirmó funcionamiento general de Brave 1.2.2.
- [ ] No subir llaves privadas, cuentas, tokens, cookies, archivos de usuario ni material descargado.

## Compilación y firma

La salida de `GENERAR_APK_WINDOWS.cmd` es una APK **debug** para pruebas, no distribución pública. La firma `debug` puede diferir entre computadoras. Crea tu propio almacén de claves privado desde Android Studio para una versión `release`, conserva copias seguras y nunca lo añadas a Git. Revisa las instrucciones actuales de Android Studio para generar la app firmada.

**Esta carpeta no incluye un APK final firmado.**
