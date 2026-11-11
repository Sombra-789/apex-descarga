# Apex Descarga

Descargas de video MP4 y audio MP3 mediante yt-dlp, con procesamiento local. Proyecto de Apex Software Inc.

## Elige tu edición

| Edición | Estado | Código y guía |
| --- | --- | --- |
| Windows con Brave | **1.2.4: corrección de compatibilidad**, pendiente de validación manual en navegador | [Instalar o actualizar](brave-windows/README_PRIMERO.md) |
| Windows con Chrome / Edge | Configuración experimental; requiere pruebas manuales | [Guía de navegadores](brave-windows/GUIA_NAVEGADORES.md) |
| Android | **1.0.1 Preview**, aplicación de pruebas independiente | [Detalles y APK](docs/ANDROID_1_0_1.md) |

**Windows 1.2.4:** Threads aparece como «sin soporte por ahora», con un mensaje claro antes de analizar o descargar. «Pestaña actual» acepta enlaces HTTP(S) de otros sitios; yt-dlp comprueba su compatibilidad. Los instaladores verifican que extensión y componente local tengan la misma versión.

[Publicaciones y descargas anteriores](https://github.com/Sombra-789/apex-descarga/releases) · [Historial](CHANGELOG.md) · [Compatibilidad y límites](docs/COMPATIBILIDAD.md)

La edición Windows 1.2.3 sigue disponible como versión anterior probada manualmente. Los ZIP publicados con ese número no contienen los cambios de 1.2.4. Para generar el paquete actual desde el código: `py -3 scripts/package_windows.py`; también está disponible como artefacto del flujo **Windows - validate and package current version** en [Actions](https://github.com/Sombra-789/apex-descarga/actions/workflows/windows-package.yml).

## Organización del repositorio

| Ruta | Contenido |
| --- | --- |
| [brave-windows/](brave-windows/) | Extensión, componente local, instaladores y pruebas Windows |
| [android/](android/) | Aplicación Android y sus herramientas |
| [docs/](docs/README.md) | Guías, compatibilidad, mantenimiento e historia |
| [scripts/](scripts/) | Empaquetado reproducible desde el código vigente |
| [.github/workflows/](.github/workflows/) | Validación y compilación de las ediciones activas |

Las recetas de publicación con versiones fijas se conservan en `docs/archive/workflows/`; ya no se ejecutan contra el código de una versión nueva. El prototipo 2.0 permanece en su [rama experimental](https://github.com/Sombra-789/apex-descarga/tree/feature/apex-descarga-2.0-alpha1/prototypes/apex-descarga-2.0). La aplicación Desktop independiente está retirada.

## Desarrollo y soporte

[Cómo contribuir y probar](CONTRIBUTING.md) · [Documentación](docs/README.md) · [Contacto](docs/guias/CONTACTO_Y_SOPORTE.md)

La compatibilidad depende del sitio y de yt-dlp; no se admiten todos los enlaces ni todos los tipos de archivo. Apex no inicia sesión ni obtiene cookies del navegador. FFmpeg es necesario para MP3 y para combinar audio/video. Consulta [privacidad](PRIVACY.md), [seguridad](SECURITY.md), [licencia GPL-3.0](LICENSE) y [avisos de terceros](THIRD_PARTY_NOTICES.md).
