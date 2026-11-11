# Apex Descarga para Windows 1.2.4

Corrección de compatibilidad pendiente de prueba manual con Brave real. Chrome y Edge siguen siendo experimentales.

## Si ya tienes Apex instalado

1. Extrae el paquete completo y cierra Brave completamente.
2. Ejecuta `ACTUALIZAR_APEX.cmd` como usuario normal.
3. Selecciona la carpeta `extension` ORIGINAL cargada en Brave. Así se conserva su ID.
4. Confirma la ruta. El actualizador respalda la extensión y el componente local antes de copiarlos; conserva la carpeta de destino, el registro y el puente EXE.
5. Abre `brave://extensions`, recarga Apex y comprueba **1.2.4 / Conectado**.

No ejecutes instaladores antiguos que incluyan `host.py` 1.0 sobre una instalación 1.2.x. Usa todos los archivos de este paquete juntos.

## Primera instalación

Requiere Windows, Python 3.12 o 3.13 x64 e Internet. FFmpeg debe estar en PATH para MP3 y combinación HD.

1. Extrae el ZIP y ejecuta `INSTALAR_POR_PRIMERA_VEZ.cmd` sin privilegios de administrador.
2. Elige navegador. El instalador prepara un entorno Python, yt-dlp y el puente local. Si ya existe una instalación, se detiene y te indica actualizar.
3. Carga la carpeta que indica el instalador desde el modo desarrollador del navegador y pega el ID solicitado.
4. Reinicia el navegador, recarga Apex y comprueba **1.2.4 / Conectado**.

## Enlaces y descargas

«Pestaña actual» acepta enlaces HTTP(S) de otros sitios. Usa «Analizar enlace» para comprobar qué puede obtener el motor. Threads muestra un aviso de falta de soporte; no se inicia una descarga. No se garantiza compatibilidad con cualquier sitio o tipo de archivo.

Si cambia el ID de la extensión, utiliza `REPARAR_APEX.cmd`. Para añadir otro navegador, consulta [GUIA_NAVEGADORES.md](GUIA_NAVEGADORES.md).

[Cambios 1.2.4](CAMBIOS_1.2.4.md) · [Compatibilidad](../docs/COMPATIBILIDAD.md) · [Privacidad y condiciones](PRIVACIDAD_Y_CONDICIONES.md)

La selección de carpeta se guarda en `settings.json`; la cola y el historial se guardan en el navegador. Apex contacta los sitios externos para analizar y descargar, sin telemetría propia ni obtención de cookies del navegador.
