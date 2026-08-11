# Photobook AI

Photobook AI es una aplicación para un tótem Android que fotografía al participante y lo integra en una escena de rally mediante inteligencia artificial.

El repositorio contiene:

- Una aplicación Android desarrollada con React Native y Expo.
- Un servidor Python pequeño que conecta la aplicación con OpenAI.
- Tres plantillas temporales en `templates/`.
- Almacenamiento de resultados en archivos, sin base de datos.

## Requisitos

- Node.js compatible con Expo SDK 57.
- pnpm.
- Python 3.11 o superior.
- Una clave de OpenAI con acceso a generación de imágenes.
- Android Studio y un emulador, o un dispositivo Android físico.

## 1. Instalar la aplicación

Desde la raíz del repositorio:

```bash
pnpm install
```

## 2. Instalar el servidor Python

Crear un entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo e instalar las dependencias:

```bash
source .venv/bin/activate
python -m pip install -r server/requirements.txt
```

En Windows PowerShell, la activación equivalente es:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r server/requirements.txt
```

## 3. Configurar las variables de entorno

Toda la configuración del servidor y de la aplicación se lee desde un único archivo `.env`. Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar `.env`:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_IMAGE_MODEL=gpt-image-2
PUBLIC_BASE_URL=http://192.168.1.50:8000

# Emulador Android
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000

# Dispositivo físico
# EXPO_PUBLIC_API_URL=http://192.168.1.50:8000
```

Variables disponibles:

- `OPENAI_API_KEY`: clave utilizada únicamente por el servidor.
- `OPENAI_IMAGE_MODEL`: modelo de generación de imágenes.
- `PUBLIC_BASE_URL`: dirección desde la que los teléfonos descargarán las imágenes del QR.
- `IMAGES_DIR`: directorio de resultados opcional. Por defecto se utiliza `generated_images/`.
- `EXPO_PUBLIC_API_URL`: dirección del servidor vista desde la aplicación Android.

`PUBLIC_BASE_URL` debe usar la IP local o dominio del equipo que ejecuta Python. No debe usar `localhost`, porque el teléfono que escanea el QR no podría acceder a esa dirección.

Para un dispositivo físico, `PUBLIC_BASE_URL` y `EXPO_PUBLIC_API_URL` normalmente tendrán la misma IP local. Para el emulador, `EXPO_PUBLIC_API_URL` debe usar `10.0.2.2`, mientras que `PUBLIC_BASE_URL` debe continuar usando una dirección accesible por los teléfonos.

El dispositivo Android, el servidor y los teléfonos que escanearán el QR deben poder comunicarse por la misma red.

## 4. Iniciar el servidor

Con el entorno virtual activado:

```bash
python -m server
```

También puede iniciarse desde macOS o Linux mediante:

```bash
pnpm server
```

El servidor escucha en `http://0.0.0.0:8000`.

Comprobar su estado:

```bash
curl http://localhost:8000/health
```

Una configuración correcta devuelve una respuesta similar a:

```json
{
  "status": "ok",
  "openai_configured": true,
  "model": "gpt-image-2"
}
```

## 5. Iniciar la aplicación Android

En otra terminal:

```bash
pnpm android
```

La cámara debe probarse en un dispositivo físico o en un emulador que tenga una cámara configurada.

## Endpoints del servidor

### Estado

```http
GET /health
```

### Generar una composición

```http
POST /api/generate
Content-Type: multipart/form-data
```

Campos:

- `scene`: `car`, `podium` o `hero`.
- `photo`: archivo JPEG, PNG o WebP de hasta 20 MB.

Respuesta:

```json
{
  "id": "identificador-aleatorio",
  "image_url": "http://servidor:8000/images/identificador-aleatorio.png"
}
```

### Descargar una imagen

```http
GET /images/<identificador>.png
```

## Ejecutar las verificaciones

Aplicación:

```bash
pnpm typecheck
pnpm export:android
```

Servidor:

```bash
pnpm server:test
```

## Almacenamiento

Las imágenes generadas se guardan en `generated_images/` con nombres aleatorios. No se utiliza una base de datos y los archivos no se eliminan automáticamente.

Para cumplir con la política de privacidad del evento, el operador debe eliminar periódicamente los archivos antiguos de este directorio.

## Seguridad de despliegue

- `.env` y `generated_images/` están excluidos del repositorio.
- La clave de OpenAI nunca debe incorporarse a la aplicación Android.
- El endpoint de generación no tiene autenticación y está diseñado para una red privada controlada.
- Si el servidor se publica en internet, debe colocarse detrás de HTTPS, autenticación y límites de solicitudes.
