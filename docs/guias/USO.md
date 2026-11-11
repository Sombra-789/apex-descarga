# Cómo utilizar Apex Descarga

Guía para Windows 1.2.4. La versión Android tiene una interfaz y publicación independientes.

## Descargar un video o audio

1. Mantén Brave abierto y abre el popup de Apex.
2. Abre la publicación concreta y pulsa **Pestaña actual**, o pega directamente su enlace HTTP(S).
3. Pulsa **Analizar enlace** para consultar el título, la miniatura y las resoluciones que el sitio permita obtener. Un fallo del análisis puede indicar incompatibilidad o restricciones del sitio.
4. Elige **MP4** para video o **MP3** para audio. MP3 requiere FFmpeg.
5. En MP4, elige la calidad deseada. Depende de los formatos disponibles; una resolución alta no mejora la fuente.
6. Mantén el modo estable como opción inicial. Si aparece HTTP 403, prueba el modo de compatibilidad HLS cuando corresponda.
7. Comprueba la carpeta de destino. **Cambiar carpeta** abre el selector de Windows; si el popup se cierra, vuelve a abrirlo para comprobar la nueva ruta.
8. Acepta las condiciones de uso y pulsa **Añadir a descargas**.
9. Espera a **Descarga completada** y pulsa **Abrir carpeta** para localizar el archivo.

## Cola, progreso e historial

- Los trabajos se procesan uno a uno; puedes añadir varios enlaces a la cola.
- Puedes cerrar el popup y volver a abrirlo para ver el progreso. Mantén el navegador abierto.
- **Cancelar** detiene la descarga activa; quitar un elemento de la cola evita que se inicie.
- La cola admite hasta 15 trabajos pendientes. El historial conserva hasta 30 registros.
- Limpiar el historial elimina los registros de la extensión; no borra los archivos descargados.
- Si el navegador o la extensión se reinician durante un trabajo, puede aparecer como interrumpido; revisa su estado antes de volver a añadirlo.

## Dónde se guardan los archivos

Sin una ruta personalizada, el destino es `%USERPROFILE%\Downloads\Apex Descarga`. La carpeta elegida se guarda en el componente local. Si estaba en una unidad desconectada, vuelve a conectarla o selecciona otro destino.

## Compatibilidad

«Pestaña actual» acepta enlaces HTTP(S); esto no garantiza que el sitio sea descargable. Usa la URL de una publicación concreta. yt-dlp determina qué puede extraer.

- **Threads:** sin soporte por ahora en Windows 1.2.4; aparece un aviso antes de analizar o descargar.
- **Otros sitios:** dependen de yt-dlp, de la disponibilidad del contenido y de las restricciones del servidor.
- **Texto, imágenes, documentos y archivos generales:** Apex no ofrece una descarga universal de esos tipos.
- No se habilitan listas de reproducción, inicio de sesión mediante cookies del navegador ni evasión de DRM.

[Instalar o actualizar](INSTALACION_WINDOWS.md) · [Solucionar problemas](SOLUCION_DE_PROBLEMAS.md) · [Compatibilidad detallada](../COMPATIBILIDAD.md)
