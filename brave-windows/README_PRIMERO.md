# Apex Descarga 1.2.3 — Brave y Windows 11

## Correccion Native Messaging

Si Brave muestra `Access to the specified native messaging host is forbidden`, normalmente el ID de la extension no coincide con `allowed_origins` del manifiesto local de Windows. La version 1.2.3 incluye `REPARAR_APEX.cmd`: revisa el componente y las dependencias, solicita el ID visible en `brave://extensions`, verifica la discrepancia, pide confirmacion antes de reparar y guarda respaldo del manifiesto. No instala paquetes ni cambia el registro. Cierra Brave completamente antes de reparar y recarga la extension despues.

Tambien puedes ejecutar el diagnostico sin cambios desde PowerShell: `powershell.exe -NoProfile -File .\windows\diagnostico.ps1 -ExtensionId ID_DE_32_LETRAS`. No se comparten IDs ni archivos de configuracion con servidores de Apex.

El actualizador `ACTUALIZAR_APEX.cmd` sigue siendo solo para actualizaciones sobre instalaciones existentes y conserva el ID de extension. Si la extension se reinstalo y cambio su ID, utiliza el reparador con autorizacion explicita.

# Apex Descarga 1.2.2 — actualización para Brave y Windows 11

## Cambios
- Conserva el diseño negro, púrpura y azul y el águila de Apex Visual Studio.
- Agrega **Cambiar carpeta** dentro de Actividad → Carpeta de destino.
- Elige la nueva ubicación mediante el selector nativo de carpetas de Windows.
- Guarda esa ubicación en `AppData\Local\ApexVideoDownloader\settings.json`; futuras descargas y «Abrir» usarán la nueva carpeta.
- Nueva información de privacidad, más transparente: no hay telemetría ni servidores propios de Apex; el historial, la configuración y los enlaces se almacenan localmente; yt-dlp debe contactar los sitios de origen.
- Solicita aceptar las condiciones revisadas antes de la próxima descarga (solo una vez por versión de términos).

## Actualización sin perder el ID ni Native Messaging
1. **Extrae** todo el ZIP. No ejecutes archivos `.cmd` directamente desde el archivo comprimido.
2. Cierra Brave completamente.
3. Ejecuta `ACTUALIZAR_APEX.cmd` **sin privilegios de administrador**, desde la cuenta de Windows que usa Brave.
4. Elige la carpeta `extension` ORIGINAL instalada en Brave, no la carpeta nueva incluida en el ZIP.
5. Confirma con `S` y espera el mensaje `ACTUALIZACION 1.2.2 APLICADA.`.
6. Abre `brave://extensions` y haz clic en **Actualizar**.
7. Abre **Apex Descarga 1.2.2** y comprueba `Conectado`.
8. En «Carpeta de destino», haz clic en **Cambiar carpeta** y elige tu carpeta. La ventana de Apex puede cerrarse al abrir el diálogo; vuelve a abrirla y comprobarás la ruta guardada.

## Datos y privacidad
Apex no envía telemetría ni datos a un servidor de Apex Visual Studio. El estado, enlaces e historial de descargas se almacenan en el navegador (almacenamiento local de la extensión), y la carpeta elegida se guarda en un JSON local en tu Windows. Para analizar o descargar, yt-dlp necesita realizar conexiones con sitios externos; también pueden cargarse miniaturas desde servicios externos. No sería correcto afirmar que no se procesa ningún dato.

## Seguridad
Usa solamente contenido autorizado. Los archivos externos pueden ser peligrosos; analiza los archivos con un antivirus. La cláusula incluida es una declaración informativa y **no sustituye asesoría legal ni garantiza exención de responsabilidad**.

## Si aparece Sin conexión
1. No reinstales Python, yt-dlp, FFmpeg ni Deno.
2. Cierra Brave por completo, ábrelo y en `brave://extensions` pulsa **Actualizar**.
3. Si sigue igual, comparte la pantalla de error y salida de `ACTUALIZAR_APEX.cmd`. No utilices reparadores de registro salvo que diagnostiquemos que sean necesarios.

## Nota técnica
Conserva `com.apex.video_downloader` como nombre del host y utiliza el mismo directorio de la extensión cargada en Brave. El actualizador respalda los archivos antes de modificarlos. No migrará los medios antiguos: permanecen en su carpeta anterior.
