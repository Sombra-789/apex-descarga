# Guía de instalación, uso y requisitos — Apex Descarga

**Producto del ecosistema Apex Software Inc.** (denominación de marca utilizada por este proyecto; no implica certificación ni acredita por sí sola una sociedad legalmente constituida).

## Para qué sirve
Gestionar descargas de vídeo MP4 y audio MP3 de contenido propio o autorizado: análisis de enlace, miniatura, calidades, cola, historial y selección de carpeta.

## Descargas disponibles
[Android 1.0.1 Preview (APK DEBUG)](https://github.com/Sombra-789/apex-descarga/releases/tag/android-v1.0.1-preview) · [Brave/Windows 1.2.3 (instalación inicial beta)](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3-instalacion-inicial) · [Brave/Windows 1.2.3 (solo actualización)](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3)

**Importante:** GitHub Actions Artifacts puede exigir inicio de sesión y caducar. Los paquetes beta/preview no se equiparan a versiones estables.

## Instalación paso a paso

### Android — primera instalación
1. Descarga el APK Android 1.0.1 Preview desde su Release oficial; no hace falta una versión anterior de Apex.
2. Abre el APK en un dispositivo con Android 10 o posterior y arquitectura ARM64; autoriza solo esa fuente de instalación si confías en su procedencia.
3. Verifica permisos, almacenamiento y conexión; esta Preview lleva firma DEBUG e identificador `.preview`, y no reemplaza la RC1 anterior.
4. **La versión Android fue probada en un Samsung Galaxy S23, pero no es exclusiva de ese teléfono.** Otros modelos compatibles también pueden instalarla, aunque no todos están verificados.

### Brave + Windows — primera instalación
1. Instala Brave y Python 3.12/3.13 x64; conecta Windows a Internet.
2. Descarga el **ZIP de instalación inicial** (no el de actualización), extráelo y ejecuta `INSTALAR_POR_PRIMERA_VEZ.cmd`.
3. En `brave://extensions`, activa Modo desarrollador, pulsa **Cargar descomprimida** y selecciona la carpeta de extensión indicada por el instalador.
4. Copia el ID de 32 letras a la consola del instalador, finaliza, reinicia Brave, recarga Apex y comprueba **Conectado**.
5. **FFmpeg es necesario para MP3 y fusión de video/audio**; se instala aparte. Deno es opcional. No exige una versión Apex anterior.

### Brave + Windows — actualización
Usa el **ZIP de actualización** solo si tienes Apex/Native Messaging previamente instalado: cierra Brave, extrae, ejecuta `ACTUALIZAR_APEX.cmd` y selecciona la carpeta original de extensión cargada en Brave. Para permisos Native Messaging, revisa `REPARAR_APEX.cmd`.

**Seguridad:** el instalador inicial se presenta como beta hasta realizar una prueba real completa de Windows/Brave, aunque supere la validación automatizada.
## Cómo funciona y cómo utilizarlo
Pega o analiza un enlace permitido, comprueba los metadatos, elige MP4 o MP3 y calidad disponible, configura la carpeta y ejecuta. Supervisa la cola, cancela o revisa el historial. En Android también puedes configurar la política de red y consultar la biblioteca.

## Requisitos y dependencias
Android: Android >=10, ARM64 (emulador x86_64), almacenamiento e internet; APK DEBUG sin firma de producción. Compilar: JDK 17/21, SDK 35, Gradle y dependencias de `android/app/build.gradle` (youtubedl-android library/ffmpeg 0.18.1). Brave: Windows 11 probado, Brave Manifest V3, Python 3.12/3.13 x64 e Internet. El paquete inicial crea un entorno Python con yt-dlp y compila localmente el host Native Messaging mediante .NET; FFmpeg se requiere aparte para MP3 y fusiones. El ZIP de actualización existente sí necesita una instalación previa. Las dependencias externas deben conservar sus respectivas licencias.

## Limitaciones, seguridad y privacidad
Los sitios pueden cambiar o bloquear extracciones; no evita DRM; requiere conectividad y espacio. MP3/mezcla pueden depender de FFmpeg. El APK Android es de pruebas; firmas diferentes impiden actualización directa. Los enlaces y metadatos se consultan en servicios externos; no prometer privacidad absoluta. La edición Desktop independiente se retiró por decisión del propietario el 28-10-2026; no se soporta ni se recomienda descargarla.

## Más información
- [Repositorio GitHub](https://github.com/Sombra-789/apex-descarga)
- [Ficha de proyecto en Notion](https://app.notion.com/p/3fb252e21ba6810790aedb0298bd09f2)
- Consulta el README y las notas de cada versión para instrucciones adicionales.

---
© 2026 Apex Software Inc. — Identidad de proyecto. Las bibliotecas externas pertenecen a sus respectivos titulares y conservan sus licencias. No se afirma registro mercantil ni afiliación con terceros.
