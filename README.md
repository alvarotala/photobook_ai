# Photobook AI

Aplicación React Native/Expo para un tótem Android vertical. La experiencia permite elegir una escena de rally, aceptar el consentimiento, tomar una fotografía guiada y visualizar el flujo de procesamiento.

## Estado actual

- Tres plantillas en `templates/`.
- Selección táctil de escena.
- Consentimiento antes de activar la cámara.
- Cámara frontal, guía facial y cuenta regresiva.
- Procesamiento simulado y vista previa de resultado.
- Repetición de foto y reinicio de sesión.
- Reinicio automático luego de 60 segundos de inactividad.

La llamada a OpenAI y la entrega pública por QR todavía no están activadas. La pantalla de resultado lo indica explícitamente para evitar confundir una plantilla con una imagen procesada.

## Ejecutar

```bash
pnpm install
pnpm android
```

La cámara debe probarse en un dispositivo Android físico o en un emulador con cámara configurada.

## Arquitectura sin backend

La app puede enviar directamente la captura y la plantilla al endpoint de edición de imágenes de OpenAI. Este enfoque es válido para un prototipo controlado, pero una clave incluida en el APK no puede considerarse secreta. La configuración prevista es ingresar la clave desde una pantalla administrativa y guardarla con Android Keystore mediante `expo-secure-store`, sin incluirla en el repositorio.

OpenAI devuelve la imagen generada codificada en Base64, no como una URL pública persistente. Por eso un teléfono no puede descargarla escaneando una supuesta URL de OpenAI. Sin backend existen dos alternativas:

1. Servir temporalmente la imagen desde el propio tótem por la red local. El teléfono y el tótem deben estar en el mismo Wi-Fi.
2. Usar un servicio externo de almacenamiento temporal. Aunque sea serverless, introduce un servicio adicional fuera de OpenAI.

La primera alternativa conserva el requisito de no tener backend propio.

## Validación

```bash
pnpm exec tsc --noEmit
pnpm exec expo export --platform android
```
