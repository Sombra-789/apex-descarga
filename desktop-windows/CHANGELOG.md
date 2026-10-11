# Historial de cambios — Apex Descarga Desktop

## 0.2.0 — UI Pro (beta)

- **Rediseño real de escritorio:** nueva cabecera, barra lateral de cinco secciones, paneles redondeados, tarjetas con sombras suaves y banner de identidad Apex.
- **Inicio:** estadísticas de completadas/en curso/pendientes, enlace y botones principales agrupados, portada y metadata en panel dedicado.
- **Descargas:** filtros, miniaturas, estados, progreso, velocidad, ETA y acciones accesibles.
- **Biblioteca:** búsqueda, filtros audio/video, abrir archivo, carpeta, copiar ruta y quitar solo del historial (sin borrar archivo físico).
- **Ajustes:** paletas, color HEX, logotipo opcional, modo compacto, ruta destino, estado de motores y botón de soporte.
- **Acerca de:** documentación, avisos y contacto `angelrlpz030207@gmail.com`.
- **Compatibilidad:** utiliza la misma carpeta de datos y formato de `jobs.json/settings.json` que la v0.1.
- **Calidad:** pruebas de motor, almacenamiento y cola; smoke de navegación gráfica y capturas de interfaz.
- **Windows:** iniciador de Python 3.11–3.13 más tolerante a instalaciones sin `py`, y salida de PyInstaller.

### Sin cambios en el motor

yt-dlp y FFmpeg, cancelación, historial, cola secuencial, almacenamiento y validación de URLs se conservan de v0.1. No se incorporó pausa/reanudación exacta, descargas paralelas ni minimización a bandeja: requerirían cambios en el motor.

### Estado

**Beta:** ejecutar la versión de Windows empaquetada y validar todas las pantallas en una máquina real antes de etiquetar estable.
