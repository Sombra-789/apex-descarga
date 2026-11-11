# Versiones y descargas

## Windows

| Versión | Disponibilidad y estado |
| --- | --- |
| **1.2.4** | Código actual en main y ZIP en artefactos de Actions. Pruebas automáticas y puente local comprobados; pendiente de aceptación manual con Brave. |
| **1.2.3** | Versión anterior con funciones validadas manualmente. Hay paquetes separados de primera instalación y de actualización. |
| Configurador Chromium 1.2.3 Preview | Publicación anterior para Brave/Chrome/Edge. Chrome y Edge siguen siendo experimentales. |

Para obtener 1.2.4 sin compilar, descarga **Code → Download ZIP** desde main, extrae todo y entra en `brave-windows/`. Sigue [la guía Windows](guias/INSTALACION_WINDOWS.md). Otra opción es el artefacto del [flujo Windows](https://github.com/Sombra-789/apex-descarga/actions/workflows/windows-package.yml), que puede caducar y requerir sesión GitHub.

**No hay un Release 1.2.4 publicado al corte de esta documentación.** Los ZIP 1.2.3 no incluyen sus cambios. Para generar un paquete limpio desde el código, usa `py -3 scripts/package_windows.py`; se escribe en `dist/` junto con su SHA-256.

Publicaciones anteriores:
- [Primera instalación Brave 1.2.3 beta](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3-instalacion-inicial).
- [Actualización Brave 1.2.3 para instalaciones existentes](https://github.com/Sombra-789/apex-descarga/releases/tag/brave-v1.2.3).
- [Configurador Chromium 1.2.3 Preview](https://github.com/Sombra-789/apex-descarga/releases/tag/chromium-v1.2.3-setup-preview1).

## Android

**1.0.1 Preview** es una aplicación de pruebas independiente. Requiere Android 10+ y ARM64; fue probada en Galaxy S23, sin ser exclusiva de ese modelo. Se instala junto a RC1 y no migra automáticamente sus datos.

1. Abre el [Release Android 1.0.1 Preview](https://github.com/Sombra-789/apex-descarga/releases/tag/android-v1.0.1-preview).
2. Descarga el APK y consulta su SHA-256.
3. Abre el APK y autoriza la instalación desde esa fuente si corresponde.
4. Confirma que estás instalando la edición Preview. Conserva RC1 si contiene información que necesitas.
5. Abre la aplicación y prueba un enlace autorizado. Las firmas DEBUG y las diferencias entre compilaciones pueden impedir actualizar una instalación anterior.

Consulta [las notas Android](ANDROID_1_0_1.md). La política de Threads añadida en Windows 1.2.4 no se trasladó automáticamente a Android.

## Ediciones históricas

La aplicación Desktop Windows independiente está retirada. Sus publicaciones 0.2.x siguen visibles como historia y no son la extensión Windows actual. El prototipo 2.0 está en una rama experimental y no descarga contenido real.

[Volver a la portada](../README.md) · [Historial](../CHANGELOG.md)
