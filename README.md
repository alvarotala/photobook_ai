# Photobook AI

Aplicación Android para un tótem fotográfico. Captura al participante, envía la fotografía a un servidor Python, genera la composición con OpenAI y muestra un QR con la URL del resultado.

El proyecto no utiliza base de datos. Las imágenes se guardan como archivos en `generated_images/`.

## Requisitos

- Node.js compatible con Expo SDK 57.
- pnpm.
- Python 3.11 o superior.
- Android Studio con Android SDK y `adb`.
- Java 17 para compilar Android.
- Una API key de OpenAI con acceso al modelo de imágenes configurado.

## Instalación

Desde la raíz del repositorio:

```bash
pnpm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r server/requirements.txt
cp .env.example .env
```

Toda la configuración se lee desde `.env`.

## Variables de entorno

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_IMAGE_MODEL=gpt-image-2
PUBLIC_BASE_URL=http://192.168.1.50:8000
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000

# Opcional
# IMAGES_DIR=./generated_images
```

- `OPENAI_API_KEY`: se utiliza únicamente en el servidor Python.
- `OPENAI_IMAGE_MODEL`: modelo usado para generar las imágenes.
- `PUBLIC_BASE_URL`: URL incluida en los QR. Debe ser accesible desde los teléfonos que descargarán el resultado.
- `EXPO_PUBLIC_API_URL`: URL del servidor incorporada a la aplicación Android.
- `IMAGES_DIR`: carpeta opcional para guardar resultados. El valor predeterminado es `generated_images/`.

Las variables `EXPO_PUBLIC_*` se incorporan al APK durante la compilación. Si cambia la URL del servidor, es necesario volver a generar el APK.

## Desarrollo local

### Servidor

```bash
pnpm server
```

El servidor escucha en el puerto `8000`. Para comprobarlo:

```bash
curl http://localhost:8000/health
```

### Android

Para el emulador estándar de Android:

```dotenv
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

Para un dispositivo físico, usar la IP LAN de la computadora:

```dotenv
EXPO_PUBLIC_API_URL=http://192.168.1.50:8000
PUBLIC_BASE_URL=http://192.168.1.50:8000
```

El dispositivo y la computadora deben estar conectados a la misma red.

Iniciar la aplicación:

```bash
pnpm android
```

La cámara del emulador puede mostrar preview correctamente y producir capturas negras. Para validar el flujo final, usar un dispositivo Android físico.

## Deploy del servidor

En producción, configurar la URL HTTP pública del servidor:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_IMAGE_MODEL=gpt-image-2
PUBLIC_BASE_URL=http://photos.example.com
EXPO_PUBLIC_API_URL=http://photos.example.com
```

Iniciar el servicio:

```bash
source .venv/bin/activate
python -m server
```

El proceso debe ejecutarse mediante un supervisor como `systemd`, Docker o el sistema utilizado por el proveedor. Puede colocarse Nginx, Caddy o un proxy equivalente delante de `localhost:8000` para publicar el servicio por HTTP.

El puerto `8000` no debe exponerse directamente a internet. El endpoint de generación no incluye autenticación propia; el proxy o la infraestructura deben aplicar límites de solicitudes y el control de acceso correspondiente.

La carpeta configurada en `IMAGES_DIR` debe ser persistente y tener permisos de escritura. Definir también una política de eliminación para las fotografías antiguas.

## Compilar el APK final

Antes de compilar, comprobar que `.env` contiene las URLs HTTP definitivas del servidor. La aplicación Android está configurada para permitir tráfico HTTP sin TLS.

### Java y Android SDK en macOS

Instalar Java 17:

```bash
brew install openjdk@17
```

Agregar estas variables a `~/.zshrc`:

```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
```

Aplicar la configuración:

```bash
source ~/.zshrc
java -version
```

### Generar y compilar Android

Desde la raíz del repositorio:

```bash
pnpm exec expo prebuild --platform android --no-install
printf 'sdk.dir=%s\n' "$ANDROID_HOME" > android/local.properties
cd android
./gradlew --stop
NODE_ENV=production ./gradlew assembleRelease
```

El APK se genera en:

```text
android/app/build/outputs/apk/release/app-release.apk
```

Instalarlo manualmente o mediante USB:

```bash
adb devices
adb install -r app/build/outputs/apk/release/app-release.apk
```

## Verificaciones

```bash
pnpm typecheck
pnpm server:test
```

Las pruebas del servidor utilizan un gateway falso y no consumen créditos de OpenAI.

## Archivos generados

Por cada experiencia, `generated_images/` contiene el resultado y los archivos enviados a OpenAI con un mismo identificador aleatorio:

```text
<id>.png
<id>-T.png
<id>-S.png
<id>-F.png
<id>-M.png
<id>-REQUEST.json
```

`.env` y `generated_images/` están excluidos del repositorio. Nunca se debe incluir la API key de OpenAI dentro del código o de un archivo versionado.
