# Apex Descarga Brave 1.2.3 — actualización para Windows

## Cambios
- Reparador guiado `REPARAR_APEX.cmd` para detectar y corregir `allowed_origins` cuando cambia el ID de la extensión de Brave.
- Diagnóstico de Native Messaging, ejecutable local, registro y herramientas externas.
- Respaldo automático del manifiesto antes de modificarlo y confirmación explícita del usuario.
- Avisos más claros en la extensión ante un error de permisos del host.
- Número de versión 1.2.3 en el manifiesto y el título de Brave.

## Compatibilidad y limitaciones
Este ZIP es una **actualización** para una instalación ya funcional. **No es un instalador completo:** no incluye un `apex_host.exe` compilado ni instala Python, FFmpeg, yt-dlp o Deno. No abras los CMD desde dentro del ZIP.

## Actualización
1. Extrae el ZIP completo.
2. Cierra Brave por completo.
3. Ejecuta `ACTUALIZAR_APEX.cmd` sin administrador.
4. Selecciona la carpeta de la extensión ORIGINAL que Brave tiene cargada; confirma la actualización.
5. Abre Brave, ve a `brave://extensions`, pulsa **Actualizar** y comprueba la versión y conexión.
6. Solo si aparece un error de acceso Native Messaging, utiliza `REPARAR_APEX.cmd` y sigue su confirmación.

## Verificación
Probado manualmente en Windows con Brave y la conexión Native Messaging. El flujo CI ejecuta comprobaciones de archivos, sintaxis JavaScript y pruebas Windows del reparador. Los resultados del CI no sustituyen pruebas en todos los equipos.

## Recuperación
El actualizador crea una copia de seguridad en `%LOCALAPPDATA%` y el reparador guarda una copia `.bak-` del manifiesto que modifica.
