# Apex Descarga para Windows 1.2.4

La extensión y el componente local usan la misma versión. Brave es la plataforma principal; Chrome y Edge siguen siendo experimentales. 1.2.4 pasó pruebas automáticas y del puente local; aún necesita aceptación manual completa en Brave.

| Tu objetivo | Abre esta guía | Ejecuta |
| --- | --- | --- |
| Primera instalación | [Requisitos y pasos](../docs/guias/INSTALACION_WINDOWS.md) | `INSTALAR_POR_PRIMERA_VEZ.cmd` |
| Actualizar una instalación existente | [Actualizar conservando el ID](../docs/guias/INSTALACION_WINDOWS.md#5-actualizar-sin-perder-el-id) | `ACTUALIZAR_APEX.cmd` |
| Descargar MP4/MP3 y gestionar la cola | [Manual de uso](../docs/guias/USO.md) | Abre Apex en el navegador |
| Reparar conexión o permisos | [Solución de problemas](../docs/guias/SOLUCION_DE_PROBLEMAS.md) | `REPARAR_APEX.cmd` cuando corresponda |
| Añadir Chrome/Edge | [Navegadores](GUIA_NAVEGADORES.md) | `AGREGAR_NAVEGADOR.cmd` |

Extrae todo el paquete antes de ejecutar los CMD. Para una primera instalación, carga la carpeta `extension` indicada por el instalador y autoriza su ID; cargar la extensión por sí sola no instala el componente Windows. Para actualizar, selecciona la carpeta de extensión ORIGINAL que ya usa Brave.

**Uso básico:** pega un enlace o toma la pestaña actual → analiza → elige MP4/MP3 y calidad → revisa la carpeta → acepta condiciones → añade a descargas. Mantén el navegador abierto y consulta el progreso.

MP3 y mezcla HD requieren FFmpeg. Threads muestra un aviso de falta de soporte. La compatibilidad con otros sitios depende de yt-dlp.

[Versiones y descargas](../docs/VERSIONES_Y_DESCARGAS.md) · [Cambios 1.2.4](CAMBIOS_1.2.4.md) · [Privacidad y condiciones](PRIVACIDAD_Y_CONDICIONES.md)
