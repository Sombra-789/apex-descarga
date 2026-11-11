# Resolver problemas de Apex Descarga

| Síntoma | Qué comprobar o hacer |
| --- | --- |
| Sin conexión / Native Messaging host not found | Comprueba que instalaste el componente Windows, además de cargar la extensión. Si ya estaba instalado, cierra Brave, vuelve a abrirlo y recarga Apex. |
| Native Messaging host is forbidden / acceso prohibido | Comprueba el ID de la tarjeta de Apex. Ejecuta `REPARAR_APEX.cmd` y sigue el diagnóstico; la reparación solicita confirmación y crea respaldo. |
| El popup dice que el componente es antiguo | Actualiza extensión y host con el mismo paquete. Usa `ACTUALIZAR_APEX.cmd` y después recarga la extensión. |
| El instalador dice que ya existe una instalación | Utiliza el actualizador. No ejecutes el instalador inicial sobre los componentes existentes. |
| Python no compatible en la primera instalación | Instala Python 3.12 o 3.13 x64 y abre una consola nueva. El instalador inicial comprueba esas versiones. |
| MP3 no funciona / falta FFmpeg | Instala FFmpeg, comprueba `ffmpeg -version` en una consola nueva y reinicia el navegador para renovar PATH. |
| HTTP 403 | Prueba el modo de compatibilidad HLS y otro formato. Si persiste, el servidor puede estar rechazando el acceso; no se garantiza solución para todos los sitios. |
| La calidad solicitada no existe | Prueba «Mejor disponible» o una resolución inferior. |
| URL no compatible o sin video | Usa el enlace al contenido concreto, no la página principal. Revisa los límites de yt-dlp y del sitio. |
| Threads muestra falta de soporte | Es el comportamiento previsto en Windows 1.2.4. Cambiar resolución o reinstalar no añade soporte a Threads. |
| Carpeta elegida no disponible | Reconecta la unidad o utiliza «Cambiar carpeta». |
| La descarga se interrumpió | Mantén el navegador abierto. Tras reiniciarlo, revisa el estado y vuelve a añadir el enlace si hace falta. |
| Chrome/Edge no conecta | Cada navegador necesita su propio registro e ID autorizado. Usa `AGREGAR_NAVEGADOR.cmd` si el componente ya existe. |

Si necesitas actualizar yt-dlp, hazlo en el **Python que realmente utiliza Apex**, no en otra instalación. Su ruta está en `%LOCALAPPDATA%\ApexVideoDownloader\python.path`. Desde PowerShell:

```powershell
$apexPython = (Get-Content -LiteralPath "$env:LOCALAPPDATA\ApexVideoDownloader\python.path" -Raw).Trim()
& $apexPython -m pip install --upgrade "yt-dlp[default]"
```

Después reinicia el navegador. Actualizar el motor no garantiza soporte para todos los sitios.

Para pedir ayuda, incluye versión de Apex, Windows/navegador, acción realizada, pasos para reproducir y texto exacto del error. [Contacto oficial](CONTACTO_Y_SOPORTE.md): apexsoftware.inc07@gmail.com.

[Instalación](INSTALACION_WINDOWS.md) · [Uso](USO.md)
