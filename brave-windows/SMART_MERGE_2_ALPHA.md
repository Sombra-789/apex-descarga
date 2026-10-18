# Apex Descarga 2.0 - Smart Merge Alpha 1

## Alcance
Primera version funcional y local para Windows 10/11 con Brave. La version estable 1.2.3 NO se modifica en main.

El usuario pega entre 2 y 100 enlaces HTTPS publicos de MediaFire cuyos archivos sigan el patron nombre.part01.rar, nombre.part02.rar, etc. El analizador ordena las partes, detecta duplicados, partes ausentes y grupos mezclados. El motor descarga hasta 4 partes en paralelo, conserva partes completas validadas mediante SHA-256, reintenta fallos y reanuda archivos parciales solo cuando la respuesta HTTP lo permite. Los enlaces caducados, privados o que requieran pasos no disponibles se rechazan.

Requiere 7-Zip previamente instalado por el usuario: comprueba integridad de RAR con 7z t, extrae en carpeta exclusiva de trabajo, revisa rutas y empaqueta los archivos extraidos en un ZIP o 7z. Prueba el archivo final con 7z t y calcula SHA-256. La limpieza de temporales es opcional y ocurre unicamente tras verificarse el archivo final.

Los archivos temporales estan en SmartMerge_Work y el resultado en SmartMerge_Output, dentro de la carpeta de destino elegida en Apex. El bufer es de 256 KiB por descarga. Limites iniciales: 16 GiB de conjunto y 16 GiB descomprimidos listados.

## Interfaz e integracion
El panel Smart Merge es desplegable y conserva toda la interfaz previa MP4, MP3, cola, historial, miniaturas, selector de carpeta y Brave Native Messaging. El motor Smart Merge utiliza un puerto independiente para cancelar y seguir su propio progreso sin usar la cola multimedia original.

## Como probar con seguridad
1. Descarga el ZIP de pruebas de GitHub Actions y extraelo.
2. Cierra Brave y no dejes descargas activas.
3. Confirma que tengas instalado 7-Zip en Windows.
4. Ejecuta ACTUALIZAR_SMART_MERGE_ALPHA.cmd sin administrador, selecciona la carpeta extension ORIGINAL que Brave usa y confirma escribiendo ALPHA.
5. Recarga Apex en brave://extensions. Abre Smart Merge, analiza las URL publicas, elige ZIP/7z y confirma que tienes permiso sobre su contenido.
6. Para regresar a la estable cierra Brave, ejecuta RESTAURAR_APEX_1_2_3.cmd, confirma RESTAURAR y recarga la extension.

El actualizador respalda los scripts previos sin modificar el ID de la extension ni el registro de Native Messaging. No desinstales la extension estable.

## Que no esta implementado
El archivo unico que genera esta Alpha se almacena en tu Windows. NO crea una URL de Internet. Para obtener un verdadero enlace unico descargable desde cualquier dispositivo se necesita un servidor que primero descargue todas las partes, las verifique y reconstruya y aloje temporalmente el archivo final. Serian necesarios permisos sobre los contenidos, limites de almacenamiento y ancho de banda, autenticacion, enlaces temporales y limpieza automatica. No hay un servidor activado en esta version.

La Alpha admite exclusivamente MediaFire publico HTTPS; el resto de proveedores queda para versiones futuras. Algunas paginas publicas pueden requerir interaccion humana, en cuyo caso el motor informa que no puede obtener el archivo. La validez del RAR solo puede comprobarse despues de completar sus partes. Esta version no ha sido aun validada con enlaces reales de MediaFire en Windows; las pruebas automatizadas usan archivos y respuestas simuladas.
