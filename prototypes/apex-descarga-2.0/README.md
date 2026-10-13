# Apex Descarga 2.0.0-alpha.1 — prototipo interactivo

Una propuesta de la nueva interfaz de Apex Descarga, creada como **aplicación web local de demostración**.

## Cómo probarlo (sin instalar nada)
1. Descarga la rama de prototipo de GitHub o abre la carpeta prototypes/apex-descarga-2.0/.
2. Descomprime los archivos manteniendo juntos index.html, styles.css, core.js y app.js.
3. Abre index.html con Brave (también funciona en otros navegadores modernos).
4. Usa cualquier URL HTTPS de ejemplo, elige MP4 o MP3, confirma los derechos sobre el contenido y añade la tarea.
5. Prueba pausar, reanudar, cancelar, buscar, filtrar, limitar operaciones simultáneas y reiniciar la demo.

Se muestran tres tareas **ficticias** inicialmente, para demostrar los estados de la interfaz.

## Límites de esta Alpha
- **NO descarga archivos** y **NO analiza URL ni contacta servicios externos**.
- **NO accede a Native Messaging**, ni a Python, FFmpeg o yt-dlp.
- Progreso, tamaños, velocidad y tiempos de espera están **simulados y claramente etiquetados**.
- Usa localStorage bajo la clave exclusiva apex-descarga-2-alpha1-demo-v1. Los trabajos que estaban activos se reabren como pausados para evitar progreso inadvertido al recargar la página.
- No abre ni altera la carpeta de descargas, la extensión instalada, el registro o allowed_origins.
- La nueva UI aún no constituye la versión estable ni un instalador.

## Tecnología
HTML, CSS y JavaScript nativos. Sin dependencias, CDN ni compilación. Compatible con abrir file:// sin servidor local ni plugins.

## Verificación de código
Si tienes Node.js 20 o posterior, ejecuta desde esta carpeta:

    node --test tests/core.test.cjs
    node --check core.js
    node --check app.js

También se ejecutan las pruebas desde GitHub Actions cuando se actualiza este prototipo.

## Ruta hacia 2.0 alpha.2
Integrar gradualmente un protocolo de eventos de progreso real sin romper la API 1.2.3. Las métricas de velocidad y reanudación reales se habilitarán solamente cuando el host Windows exponga datos verificables. Mantener permisos mínimos y pruebas de extremo a extremo.
