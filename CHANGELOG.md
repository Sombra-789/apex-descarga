# Historial de cambios

## Brave + Windows 1.2.3 — ESTABLE (2026-10-13)
- Se declara concluido el desarrollo principal de Apex Descarga, con Brave/Windows v1.2.3 como referencia estable de esa plataforma.
- Se incluye diagnóstico y reparación de Native Messaging mediante REPARAR_APEX.cmd, con consentimiento y respaldo del manifiesto.
- El usuario confirmó conexión, descargas MP4/MP3, miniaturas, carpetas y administración de cola e historial en Windows.
- Las pruebas automatizadas de la versión y reparador fueron aprobadas en GitHub Actions.
- Se preparó la publicación de un ZIP de actualización verificable en GitHub Releases (no instalador de primera instalación).
- El desarrollo 2.0 alpha.1 queda reservado como prototipo experimental sin fusionarlo con estable.

### Estado de las otras plataformas
- Android 1.0.0-rc1: APK de pruebas DEBUG disponible en GitHub Releases; no debe confundirse con Brave 1.2.3.
- Windows Desktop 0.2.1: beta independiente, no se declara estable.
- Próximas modificaciones: mantenimiento, correcciones y actualizaciones menores si fueran necesarias.


## 1.0.0-rc1 (candidato) — 2026-10-11
- Se crea un monorepositorio con fuentes recuperadas de Android y Brave/Windows.
- Android: `versionCode` 8 y `versionName` 1.0.0-rc1; mismas preferencias, `applicationId` y motor de 0.6.
- Se añade pipeline CI para pruebas de host/extensión y compilación Android **debug**, junto a documentación de privacidad, seguridad, licencias y publicación.
- No se modifica la lógica central de descargas. Firma y validación final **pendientes**.

## Android 0.6 UI Pro
- Navegación inferior Inicio/Cola/Biblioteca/Ajustes; rediseño Figma.

## Android 0.5
- Control Wi-Fi y datos, compartir enlace, metadatos MP3, actualización del motor y mejores estados.

## Android 0.4
- Portadas y vista previa, cola rediseñada, biblioteca y búsqueda.

## Android 0.3
- Cola, segundo plano, notificaciones, temas HEX y logotipo opcional.

## Android 0.2/0.1
- Base funcional MP4/MP3, correcciones de formato, diagnóstico y FFmpeg.

## Brave/Windows 1.2.2 — código fuente actualizado
- Se incorpora el paquete oficial aportado por el propietario para Brave 1.2.2: extensión, Native Messaging, actualizador Windows, iconos y pruebas.
- Selector nativo de carpeta y ruta de descarga persistente en `settings.json`.
- Avisos de privacidad y condiciones revisados, aceptación una vez por versión de términos.
- Actualización de iconos sin cambiar identidad visual o ID existente de extensión.

## Brave/Windows 1.2.0
- Vista previa multimedia, cola secuencial, historial y integración Native Messaging con Python.
