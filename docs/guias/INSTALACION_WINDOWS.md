# Instalar o actualizar Apex Descarga en Windows

Esta guía corresponde al código **1.2.4** de la extensión y del componente local. Brave es el navegador principal; Chrome y Edge tienen configuración experimental. Windows 1.2.3 conserva su validación manual anterior; 1.2.4 pasó pruebas automáticas y comprobaciones del puente local, pero aún requiere aceptación manual en Brave.

**Ayuda para instalar:** [apexsoftware.inc07@gmail.com](mailto:apexsoftware.inc07@gmail.com).

## Qué vas a instalar

Apex tiene dos partes que deben trabajar juntas: un botón dentro del navegador (la extensión) y un pequeño programa en Windows que realiza la descarga. El instalador prepara ese programa; después te pide añadir y autorizar el botón del navegador. Necesitas completar ambos pasos.

Los archivos terminados en `.cmd` se abren con doble clic. Se mostrará una ventana con instrucciones; mantenla abierta hasta que termine.

## 1. Elegir el procedimiento

| Tu situación | Archivo que debes ejecutar |
| --- | --- |
| Nunca has instalado Apex en esta cuenta de Windows | `INSTALAR_POR_PRIMERA_VEZ.cmd` |
| Apex ya funciona o existe su componente local | `ACTUALIZAR_APEX.cmd` |
| Cambió el ID de la extensión y aparece acceso prohibido | `REPARAR_APEX.cmd` |
| Apex funciona en Brave y quieres añadir Chrome o Edge | `AGREGAR_NAVEGADOR.cmd` |

La primera instalación se detiene si detecta componentes previos. No mezcles un ZIP antiguo con archivos nuevos.

## 2. Obtener todos los archivos de 1.2.4

1. Abre el [repositorio oficial](https://github.com/Sombra-789/apex-descarga).
2. Pulsa el botón verde **Code** y después **Download ZIP**. En el Explorador de archivos, haz clic derecho sobre el ZIP descargado, elige **Extraer todo** y confirma la carpeta de destino.
3. Abre la carpeta extraída, después `apex-descarga-main` y luego `brave-windows`. Allí encontrarás los archivos de instalación. «Código» se refiere a los archivos del proyecto; no tienes que modificarlos ni programar.
4. Ejecuta los archivos desde la carpeta extraída, nunca desde el ZIP.

También puedes descargar el artefacto **Apex-Descarga-Windows** de una ejecución exitosa del [flujo de empaquetado](https://github.com/Sombra-789/apex-descarga/actions/workflows/windows-package.yml). GitHub puede exigir iniciar sesión y los artefactos caducan. Si contiene un ZIP interno, extráelo también.

**Distribución:** 1.2.4 está en el código y en los artefactos de Actions. Los Releases con número 1.2.3 son anteriores y no incluyen el aviso de Threads de 1.2.4. Consulta [versiones y descargas](../VERSIONES_Y_DESCARGAS.md).

## 3. Requisitos para una primera instalación

- Windows x64 y Brave; Chrome/Edge se mantienen experimentales.
- **Python 3.12 o 3.13 de 64 bits**, que son las versiones admitidas por el instalador inicial. Python es una herramienta que Apex necesita para funcionar. Descarga una de esas versiones desde [python.org para Windows](https://www.python.org/downloads/windows/), abre su instalador y sigue las instrucciones. Una versión con número mayor no sustituye este requisito del instalador de Apex.
- Internet para que el instalador cree el entorno Python e instale yt-dlp.
- **FFmpeg**, una herramienta que Apex utiliza para crear MP3 y unir video/audio de alta calidad. Debe estar disponible para otros programas en Windows; a esto se le llama estar «en PATH».

Para instalar FFmpeg, abre el menú Inicio, escribe **PowerShell**, abre la aplicación, copia el siguiente comando y pulsa **Enter**:

```powershell
winget install --id Gyan.FFmpeg -e
```

Después abre una consola nueva, comprueba `ffmpeg -version` y reinicia el navegador. Deno puede ser necesario para determinados sitios; no lo instala este procedimiento automáticamente.

## 4. Primera instalación, paso a paso

1. Haz doble clic en `INSTALAR_POR_PRIMERA_VEZ.cmd`. No hace falta elegir «Ejecutar como administrador».
2. Elige Brave (opción principal) o el navegador experimental correspondiente.
3. Espera mientras se prepara el entorno local, yt-dlp, el componente Python y el puente Native Messaging.
4. Cuando el instalador lo indique, abre `brave://extensions` y activa **Modo desarrollador**.
5. Pulsa **Cargar descomprimida** y selecciona **exactamente la carpeta extension indicada por el instalador**. Habitualmente será `%LOCALAPPDATA%\ApexVideoDownloader\extension`.
6. Busca **ID** en la tarjeta de Apex: es un código de 32 letras que identifica la extensión. Cópialo, vuelve a la ventana del instalador, pégalo donde lo solicita y pulsa **Enter** para terminar.
7. Cierra Brave completamente, vuelve a abrirlo y recarga Apex desde la página de extensiones.
8. Abre el icono de Apex. Debe mostrar **V1.2.4** y **Conectado**.

Para Chrome usa `chrome://extensions`; para Edge, `edge://extensions`. Cada navegador necesita autorizar su propio ID. Cargar solo la extensión sin instalar y registrar el componente Windows produce «Sin conexión».

## 5. Actualizar sin perder el ID

1. Extrae todo el código o paquete nuevo en una carpeta distinta.
2. Cierra Brave completamente y ejecuta `ACTUALIZAR_APEX.cmd` desde el paquete nuevo.
3. Selecciona la carpeta **extension ORIGINAL que Brave ya tiene cargada**, no la copia nueva.
4. Revisa la ruta y confirma con `S`. El actualizador crea respaldos antes de copiar.
5. Abre Brave, entra en `brave://extensions` y pulsa el botón de recarga de Apex.
6. Comprueba **V1.2.4 / Conectado** y prueba un enlace conocido.

Se conservan la carpeta de descarga configurada, las autorizaciones y el puente instalado. Mantener la misma carpeta de extensión conserva su ID. No muevas ni renombres esa carpeta después.

## 6. Comprobar que quedó bien

- La tarjeta y el popup muestran 1.2.4; no aparece aviso de componente antiguo.
- Un enlace autorizado conocido permite analizar metadatos y descargar.
- Con FFmpeg disponible puedes crear un MP3.
- «Cambiar carpeta» guarda la ruta y «Abrir carpeta» abre el destino.
- Threads muestra «Las descargas de Threads todavía no están disponibles en Apex Descarga.»

[Cómo utilizarlo](USO.md) · [Resolver problemas](SOLUCION_DE_PROBLEMAS.md) · [Guía de navegadores](../../brave-windows/GUIA_NAVEGADORES.md)

## Si necesitas ayuda

Escribe a **[apexsoftware.inc07@gmail.com](mailto:apexsoftware.inc07@gmail.com)**. Indica en qué paso te quedaste y copia el mensaje que aparece. Puedes adjuntar una captura de pantalla.

Ejemplo: «Estoy instalando Apex Descarga en Windows 11 con Brave. En el paso 6 aparece este mensaje: …».
