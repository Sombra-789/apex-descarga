# Apex Descarga 1.2.3 — instalar la extensión en Windows

## Qué significa la compatibilidad con Chromium

Chrome, Microsoft Edge y Brave se basan en Chromium, por lo que comparten gran parte de la tecnología de extensiones. Apex utiliza esa base común.

Aun así, Apex también necesita conectarse con un programa instalado en Windows. El instalador debe registrar esa conexión para el navegador elegido y autorizar el ID que corresponda. Por eso, compartir Chromium no sustituye una prueba completa de instalación y descarga en cada navegador.

**La validación pendiente corresponde a Apex en Chrome/Edge; no significa que esos navegadores sean experimentales.**

**Android es otra edición:** se instala como una aplicación móvil independiente (APK), no como una extensión del navegador. Su estado Preview y sus actualizaciones se documentan por separado.

Referencias técnicas: [Microsoft Edge — Native Messaging](https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/developer-guide/native-messaging) y [Chrome — Native Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging).

**Apex Software Inc.** · [Contacto y soporte](../docs/guias/CONTACTO_Y_SOPORTE.md): **apexsoftware.inc07@gmail.com**.

## Navegadores y estado

| Navegador | Instalación | Estado |
| --- | --- | --- |
| **Brave** | `brave://extensions` | Principal; v1.2.3 validada en instalaciones previas |
| **Google Chrome** | `chrome://extensions` | Base Chromium compatible; validación manual de Apex pendiente |
| **Microsoft Edge** | `edge://extensions` | Base Chromium compatible; validación manual de Apex pendiente |
| **Vivaldi / Opera / otros Chromium** | No se incluye instalador específico | Sin pruebas ni soporte declarado; no asumir compatibilidad |
| **Firefox / Safari** | No admiten este paquete Chromium tal como está | Requerirían otra implementación |

La extensión es **Manifest V3** y usa **Native Messaging** con un programa local en Windows. Copiar solo la extensión **no basta**: el instalador registra el host de Windows en el navegador elegido. Cada navegador tiene su propia clave de registro y su propio ID de extensión. Chrome y Edge no se consideran probados aún en uso real.

## Primera instalación (sin una versión anterior de Apex)

1. Instala Windows 11, un navegador compatible de la tabla, Python 3.12 o 3.13 **x64**, y ten Internet.
2. Descarga y extrae **el paquete completo de configuración para navegadores** desde [GitHub Releases](https://github.com/Sombra-789/apex-descarga/releases/tag/chromium-v1.2.3-setup-preview1). **No utilices el antiguo ZIP de actualización 1.2.3**, que exige un Apex anterior.
3. Ejecuta `INSTALAR_POR_PRIMERA_VEZ.cmd` como usuario normal. Elige **Brave (1), Chrome (2) o Edge (3)**. El instalador prepara Python, instala yt-dlp en un entorno aislado y compila el puente local de Native Messaging.
4. En el navegador elegido abre `brave://extensions`, `chrome://extensions` o `edge://extensions`; activa **Modo desarrollador** y selecciona **Cargar descomprimida / Load unpacked**. Elige la carpeta **extension** que informa el instalador, normalmente `%LOCALAPPDATA%\ApexVideoDownloader\extension`.
5. Copia el ID de 32 letras que aparece junto a Apex Descarga en el navegador. Vuelve a la consola, pega el ID y finaliza. Cierra **todas las ventanas y procesos** de ese navegador, vuelve a abrirlo y recarga Apex en su pantalla de extensiones.
6. Pulsa el icono de Apex Descarga, acepta las condiciones y verifica que aparezca **Conectado**. Para MP3 o unir video/audio HD, **FFmpeg** debe instalarse por separado y figurar en `PATH` (comprueba `ffmpeg -version`). Deno es opcional según el sitio.

## Añadir otro navegador si ya instalaste Apex

1. En el navegador adicional, abre su página `...://extensions` y carga la **misma** carpeta `%LOCALAPPDATA%\ApexVideoDownloader\extension`.
2. Ejecuta `AGREGAR_NAVEGADOR.cmd` desde el paquete de configuración actualizado. Elige Brave, Chrome o Edge e introduce el **ID de extensión mostrado por ese navegador**.
3. Confirma: Apex conserva los IDs autorizados anteriores y añade únicamente el nuevo ID a `allowed_origins`; registra el host en la ruta de ese navegador. Cierra y reabre el navegador añadido; recarga la extensión.
4. Si recibes `Access to the specified native messaging host is forbidden`, confirma que el ID coincida exactamente y que la clave de registro corresponda a ese navegador. Consulta el diagnóstico; si hay varios IDs, utiliza `AGREGAR_NAVEGADOR.cmd` en lugar del reparador antiguo, que intencionalmente evita modificar permisos múltiples.

## Actualizar Brave si ya tenías una versión anterior

El [ZIP de actualización 1.2.3](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3) y `ACTUALIZAR_APEX.cmd` son **solo** para una instalación Brave existente y conservan su configuración. No son la vía de primera instalación.

## Requisitos y límites

- Windows x64; Python 3.12/3.13 x64, Internet para instalar yt-dlp, Brave/Chrome/Edge actual con Manifest V3. El puente nativo se compila con .NET Framework en Windows.
- Uso para contenido propio o autorizado. No se soporta DRM, playlists ni compatibilidad universal con todos los sitios.
- Firefox, Safari, navegadores móviles y Chromium alternativos no están habilitados por este instalador. El soporte de Apex en Chrome y Edge sigue pendiente de validación manual completa.
- Mantén la carpeta instalada y no la muevas tras cargar la extensión. Las políticas corporativas pueden impedir extensiones sin empaquetar o Native Messaging.
- No envíes contraseñas, cookies, tokens ni capturas con información privada por correo.

[Contactar a Apex Software Inc.](mailto:apexsoftware.inc07@gmail.com) — sugerencias, quejas y errores.
