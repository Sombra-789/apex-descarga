# Cierre del desarrollo principal — Apex Descarga

**Decisión del responsable:** el proyecto se considera completado en su etapa de desarrollo principal. A partir de ahora se mantiene para correcciones y actualizaciones menores.

## Versiones y distribución

| Plataforma | Estado | Artefacto |
| --- | --- | --- |
| Brave + Windows 11 (primera instalación) | **1.2.3, instalador beta** | https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3-instalacion-inicial |
| Brave + Windows 11 (actualización) | **1.2.3 estable** (validada sobre instalación previa) | https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3 |
| Android | **1.0.0-rc1 de pruebas, NO estable** | https://github.com/Sombra-789/apex-descarga/releases/tag/v1.0.0-rc1 |
| Desktop Windows independiente | **RETIRADA (28-10-2026)** | Código y CI eliminados de main; releases históricos pendientes de retirada |
| Prototipo UI 2.0 alpha.1 | **Experimental, congelado en rama separada** | https://github.com/Sombra-789/apex-descarga/pull/7 |

El APK Android es DEBUG. La edición Android se probó en un Samsung Galaxy S23, pero no es exclusiva de ese teléfono. Su versión no equivale a la versión Brave/Windows 1.2.3. El paquete de Brave es una **actualización**, no un instalador desde cero.

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
- Las publicaciones mantienen etiquetas diferenciadas por plataforma para no confundir usuarios: brave-v* y android-v*; los antiguos desktop-v* quedan obsoletos y pendientes de eliminación de Releases.
- Evitar publicar APK con etiqueta «estable» sin firma release propia y proceso adecuado de verificación.

## Descargas

- **[APK Android 1.0.0-rc1 DEBUG](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk)**
- **[SHA-256 del APK](https://github.com/Sombra-789/apex-descarga/releases/download/v1.0.0-rc1/Apex-Descarga-Android-1.0.0-rc1-DEBUG-TESTING.apk.sha256)**
- **[ZIP Brave/Windows 1.2.3 estable](https://github.com/Sombra-789/apex-descarga/releases/download/brave-v1.2.3/Apex-Descarga-Brave-1.2.3-Actualizacion.zip)**

Los archivos se sirven desde GitHub Releases, no se copian binarios al árbol del repositorio.
