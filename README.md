# Apex Descarga

Apex Descarga permite guardar en tu computadora un video o solo su audio a partir de un enlace compatible. En Windows se utiliza desde una extensión, es decir, un botón que se añade al navegador. Proyecto de Apex Software Inc.

**¿Necesitas ayuda para instalar o descargar?** Escribe a **[apexsoftware.inc07@gmail.com](mailto:apexsoftware.inc07@gmail.com)**.

## Antes de empezar

- **MP4** guarda el video con su audio; **MP3** guarda solo el audio.
- Si es tu primera vez, sigue la guía de instalación desde el principio. No necesitas saber programar.
- Si ya usas Apex, elige la guía de actualización para conservar tu instalación.
- No todos los sitios permiten descargar contenido. Threads no tiene soporte por ahora en Windows 1.2.4.

## Empieza aquí

| Qué necesitas | Guía |
| --- | --- |
| Instalar por primera vez en Windows | [Requisitos y pasos de instalación](docs/guias/INSTALACION_WINDOWS.md#4-primera-instalación-paso-a-paso) |
| Actualizar Apex sin cambiar el ID | [Actualizar una instalación existente](docs/guias/INSTALACION_WINDOWS.md#5-actualizar-sin-perder-el-id) |
| Aprender a descargar, cambiar carpeta y gestionar la cola | [Manual de uso](docs/guias/USO.md) |
| Resolver conexión, FFmpeg, formatos o errores del sitio | [Solución de problemas](docs/guias/SOLUCION_DE_PROBLEMAS.md) |
| Instalar la edición Android | [Versiones, APK y precauciones de actualización](docs/VERSIONES_Y_DESCARGAS.md#android) |

## Ediciones y estado

| Edición | Versión y estado | Obtenerla |
| --- | --- | --- |
| **Windows + Brave** | **1.2.4**, mantenimiento; pruebas automáticas y puente local comprobados, pendiente de aceptación manual en Brave | [Código main](https://github.com/Sombra-789/apex-descarga/archive/refs/heads/main.zip) o [artefacto Windows de Actions](https://github.com/Sombra-789/apex-descarga/actions/workflows/windows-package.yml) |
| Windows + Chrome/Edge | Configuración experimental, pendiente de pruebas manuales | [Guía de navegadores](brave-windows/GUIA_NAVEGADORES.md) |
| **Android** | **1.0.1 Preview**, APK de pruebas independiente | [Release Android](https://github.com/Sombra-789/apex-descarga/releases/tag/android-v1.0.1-preview) |

**Para obtener Windows 1.2.4:** abre el botón verde **Code** de este repositorio, elige **Download ZIP**, haz clic derecho en el archivo descargado y selecciona **Extraer todo**. Abre la carpeta extraída, después `apex-descarga-main` y luego `brave-windows`. Ejecuta `INSTALAR_POR_PRIMERA_VEZ.cmd` si nunca has instalado Apex o `ACTUALIZAR_APEX.cmd` si ya existe una instalación. Sigue la [guía completa](docs/guias/INSTALACION_WINDOWS.md) para cargar y autorizar la extensión correctamente.

La versión anterior **Windows 1.2.3** conserva sus pruebas manuales. Sus Releases no contienen los cambios de 1.2.4. [Versiones y descargas](docs/VERSIONES_Y_DESCARGAS.md).

## Uso rápido en Windows

1. Abre una publicación concreta y pulsa **Pestaña actual**, o pega su enlace.
2. Usa **Analizar enlace** para consultar los datos disponibles.
3. Selecciona **MP4** o **MP3** y, para video, la calidad.
4. Comprueba la carpeta de destino, acepta las condiciones y pulsa **Añadir a descargas**.
5. Mantén el navegador abierto y, al terminar, pulsa **Abrir carpeta**.

**Requisitos:** Python 3.12/3.13 x64 para la primera instalación; Internet; FFmpeg en PATH para MP3 y combinación HD. Deno puede ser necesario en determinados sitios.

**Compatibilidad:** depende de yt-dlp y del sitio. Windows 1.2.4 identifica **Threads como sin soporte por ahora**. No es un descargador universal de texto, imágenes, documentos o archivos generales; no inicia sesión mediante cookies del navegador ni elude DRM. [Límites completos](docs/COMPATIBILIDAD.md).

## Organización del repositorio

| Carpeta | Contenido |
| --- | --- |
| [brave-windows/](brave-windows/) | Extensión, componente Windows, instaladores y pruebas |
| [android/](android/) | Aplicación Android y herramientas |
| [docs/guias/](docs/guias/) | Instalación, uso, solución de problemas y soporte |
| [docs/mantenimiento/](docs/mantenimiento/) | Identidad y lista de publicación |
| [docs/archive/](docs/archive/) | Recetas históricas de publicación |
| [scripts/](scripts/) | Empaquetado del código vigente |
| [.github/workflows/](.github/workflows/) | Pruebas y compilaciones activas |

La edición Desktop independiente está retirada. El [prototipo 2.0](https://github.com/Sombra-789/apex-descarga/tree/feature/apex-descarga-2.0-alpha1/prototypes/apex-descarga-2.0) es experimental y simula descargas.

[Índice de documentación](docs/README.md) · [Historial](CHANGELOG.md) · [Contribuir y probar](CONTRIBUTING.md) · [Contacto](docs/guias/CONTACTO_Y_SOPORTE.md) · [Privacidad](PRIVACY.md) · [Seguridad](SECURITY.md) · [Licencia](LICENSE) · [Dependencias](THIRD_PARTY_NOTICES.md)
