# Notas internas de desarrollo

Este archivo contiene decisiones, recordatorios y trabajo pendiente del equipo. La documentación necesaria para instalar y ejecutar el repositorio debe permanecer en `README.md`.

## Estado actual

- La aplicación Android está conectada a `POST /api/generate`.
- La pantalla final muestra la imagen generada y un QR con `image_url`.
- El servidor guarda resultados en `generated_images/` con nombres aleatorios.
- Las pruebas del servidor utilizan un gateway falso y no consumen créditos de OpenAI.
- Cada escena genera una máscara RGBA en memoria. La zona transparente cubre al sujeto placeholder y obliga a OpenAI a editar esa región usando la captura como segunda referencia.

## Pendientes

- Repetir una generación completa después de incorporar las máscaras y evaluar la preservación de identidad en las tres escenas.
- Ajustar los prompts después de revisar resultados reales.
- Definir la política de retención y agregar limpieza automática cuando se conozca el tiempo requerido por el evento.
- Agregar autenticación o un token de instalación antes de exponer el servidor fuera de una red privada.
- Evaluar límites de solicitudes para evitar consumo accidental o malicioso.
- Configurar modo kiosco y arranque automático en el dispositivo Android definitivo.
- Sustituir las plantillas temporales cuando se entreguen los recursos finales.
- Confirmar resolución, relación de aspecto y orientación exactas de la pantalla del tótem.

## Convención de documentación

- `README.md`: instalación, configuración, inicio, uso y resolución de problemas para usuarios del repositorio.
- `DEV_NOTES.md`: decisiones internas, experimentos, pendientes y recordatorios del equipo.
- Todos los secretos y valores específicos de cada instalación deben permanecer en el único archivo ignorado `.env`.
