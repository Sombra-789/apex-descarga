# Código fuente Brave/Windows 1.2.2 — confirmado

El contenido de `brave-windows/` procede del paquete **APEX_DESCARGA_1.2.2_ACTUALIZACION(1).zip**, facilitado por el propietario como la actualización más reciente. Contiene la extensión Manifest V3, sus iconos, el host Python Native Messaging, el actualizador Windows (PowerShell y CMD) y los tests correspondientes.

- `extension/manifest.json`: `version` = `1.2.2`.
- `windows/host.py`: `VERSION = '1.2.2'`.
- Permisos de extensión: `activeTab`, `nativeMessaging` y `storage`.
- Novedades verificables en código: selección de carpeta de descarga mediante diálogo nativo Windows; persistencia en `settings.json`, confirmación de nuevos términos y avisos de privacidad; copia de iconos por el actualizador.
- Para actualizar una instalación previa sin perder el ID de Brave, usar la guía en `README_PRIMERO.md` y su script `ACTUALIZAR_APEX.cmd`.
- Este snapshot procede de un **paquete de actualización**: puede requerir una instalación previa ya configurada de Native Messaging para usar todas las funciones. No equivale a un instalador completo desde cero.

Los archivos `CAMBIOS_1.2.md` documentan historia previa; `CAMBIOS_1.2.2.md` contiene las notas de esta versión.
