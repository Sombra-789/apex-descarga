# Cierre del desarrollo principal — Apex Descarga

**Decisión del responsable:** el proyecto se considera completado en su etapa de desarrollo principal. A partir de ahora se mantiene para correcciones y actualizaciones menores.

## Versiones y distribución

| Plataforma | Estado | Artefacto |
| --- | --- | --- |
| Brave + Windows 11 | **1.2.3 estable** (uso y funcionamiento confirmados) | https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3 |
| Android | **1.0.0-rc1 de pruebas, NO estable** | https://github.com/Sombra-789/apex-descarga/releases/tag/v1.0.0-rc1 |
| Desktop Windows independiente | **0.2.1 Beta** | https://github.com/Sombra-789/apex-descarga/releases/tag/desktop-v0.2.1-beta |
| Prototipo UI 2.0 alpha.1 | **Experimental, congelado en rama separada** | https://github.com/Sombra-789/apex-descarga/pull/7 |

El APK de Android es DEBUG y su versión no equivale a la versión estable Brave 1.2.3. El paquete de Brave es una **actualización**, no un instalador desde cero.

## Funciones confirmadas por el usuario en Brave + Windows

- Estado de conexión Brave/Windows con Native Messaging.
- Vista previa de enlaces y miniaturas.
- Descargas MP4 y conversión MP3.
- Cambio y apertura de carpeta destino.
- Cola, historial y cancelación.
- Reparación de un cambio de ID de extensión mediante REPARAR_APEX.cmd.

## Calidad y seguridad

Se aprobaron comprobaciones automáticas de la extensión y el host y las pruebas específicas de reparación Native Messaging en GitHub Actions. La compilación estable del ZIP ejecuta nuevamente estos controles y publica hash SHA-256. Las pruebas no garantizan compatibilidad universal, seguridad absoluta de contenido externo ni funcionamiento de todos los servicios.

La versión Android 1.0 RC1 conserva advertencias propias de software de pruebas: firma de depuración, validación limitada y necesidad de revisar licencias y distribución.

## Política de mantenimiento

- La rama main contiene la versión de referencia, la documentación y los flujos de publicación.
- Se aceptarán parches menores, correcciones de vulnerabilidades y ajustes de dependencias.
- No se seguirá con la UI 2.0 ni se alterará el host estable sin una decisión explícita futura.
- Las publicaciones mantienen etiquetas diferenciadas por plataforma para no confundir usuarios: brave-v*, v1.0.0-rc1 (Android) y desktop-v*.
- Evitar publicar APK con etiqueta «estable» sin firma release propia y proceso adecuado de verificación.

## Descargas

- **[APK Android 1.0.0-rc1 DEBUG](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk)**
- **[SHA-256 del APK](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk.sha256)**
- **[ZIP Brave/Windows 1.2.3 estable](https://github.com/Sombra-789/apex-descarga/releases/download/brave-v1.2.3/Apex-Descarga-Brave-1.2.3-Actualizacion.zip)**

Los archivos se sirven desde GitHub Releases, no se copian binarios al árbol del repositorio.
