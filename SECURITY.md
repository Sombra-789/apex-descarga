# Seguridad / Security policy

## Estado
El proyecto está en **candidato 1.0** y no mantiene todavía un programa público de divulgación coordinada. No publiques en issues enlaces privados, tokens, contraseñas, cookies, archivos de firma ni datos personales.

## Diseño
- El host Brave restringe entradas a URLs HTTP(S), invoca herramientas sin `shell=True` y no importa cookies del navegador.
- La aplicación Android evita tráfico HTTP sin cifrar y no solicita permisos globales de archivos.
- yt-dlp y FFmpeg son componentes externos: su superficie de actualización, dependencias y binarios requieren vigilancia.

## Antes de la distribución
Revisar dependencias, configuración del motor actualizable, URLs recibidas, manejo de rutas y carga de miniaturas; agregar un contacto de seguridad privado del mantenedor. Si encuentras una falla, contacta al mantenedor por un canal privado de confianza en vez de publicar instrucciones de explotación.
