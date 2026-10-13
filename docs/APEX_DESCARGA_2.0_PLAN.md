# Apex Descarga 2.0 — plan inicial

**Estado:** propuesta técnica, no implementado. **Alcance:** extensión Brave y host Windows. No modifica Android ni la aplicación desktop.

## Objetivo
Convertir Apex en un administrador de descargas claro, veloz y fiable sin romper la conexión Native Messaging ni cambiar innecesariamente el ID de la extensión.

## Prioridades
1. **Diseño:** interfaz moderna y adaptable, panel de actividad, estados de progreso, búsqueda de historial y manejo de errores explicativo.
2. **Descargas:** cola persistente, concurrencia configurable con límites seguros, velocidad instantánea/promedio, tiempo estimado real (si se conoce) y reintentos controlados.
3. **Calidad:** tests de protocolo host ↔ extensión, validación de entradas, cancelaciones y errores de yt-dlp/FFmpeg. Evitar declarar compatibilidad con sitios sin probarlos.
4. **Seguridad:** descargas autorizadas, verificación de rutas de salida, protección de datos locales, permisos mínimos y no ejecución de comandos arbitrarios.
5. **Empaquetado:** ZIP de actualización reproducible, checksum SHA-256, documentación de versión y pruebas automáticas antes de publicación.

## Fases propuestas
- **2.0.0-alpha.1:** prototipo UI aislado, sin reemplazar la 1.2.3.
- **2.0.0-alpha.2:** protocolo de trabajos/estados con tests.
- **2.0.0-beta.1:** concurrencia controlada, reanudación cuando el origen lo permita y pruebas en Windows/Brave.
- **2.0.0:** revisión, notas de cambios, instalación y migración desde 1.2.3.

## Criterios de aceptación
- Mantener la conexión con Brave y la instalación existente.
- MP4, MP3, selección de carpeta, historial y cancelación sin regresiones.
- Sin nuevos permisos de navegador sin justificación explícita.
- Manejo visible de fallos; no inventar velocidades, tiempos ni garantías de reanudación.
- CI aprobado, validación manual en Windows y paquete de actualización reproducible.

No se fusionarán cambios de 2.0 en la versión estable hasta que estén probados.
