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
OPENAI_IMAGE_PROFILE=balanced
PUBLIC_BASE_URL=http://192.168.1.50
EXPO_PUBLIC_API_URL=http://10.0.2.2

# Opcional
# IMAGES_DIR=./generated_images
```

- `OPENAI_API_KEY`: se utiliza únicamente en el servidor Python.
- `OPENAI_IMAGE_MODEL`: modelo usado para generar las imágenes.
- `OPENAI_IMAGE_PROFILE`: perfil `fast`, `balanced` o `quality` usado por el servidor.
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

### Medir la velocidad de OpenAI y xAI

El benchmark de OpenAI envía la plantilla y la foto del sujeto. El de xAI elimina
localmente al placeholder de la plantilla y envía el sujeto primero, la plantilla
recortada segunda y un recorte facial como tercera referencia. xAI no recibe un archivo
de máscara separado.

OpenAI:

```bash
.venv/bin/python -m server.benchmark_openai /path/a/la/foto.jpg car --profile fast
```

Perfiles disponibles: `fast` usa `1152x640`, calidad baja y JPEG; `balanced` usa
`1536x1024`, calidad media y JPEG; `quality` reproduce la salida original de calidad
alta en PNG. El servidor usa el perfil indicado por `OPENAI_IMAGE_PROFILE` y su valor
predeterminado es `balanced`. El benchmark usa `fast` si se omite `--profile`. Las
definiciones de los perfiles están centralizadas en `server/image_profiles.py`.

xAI:

```bash
.venv/bin/python -m server.benchmark_xai /path/a/la/foto.jpg car
```

El segundo argumento es la escena: `car`, `podium` o `hero`. Los comandos muestran
el tiempo de preparación, el tiempo del proveedor y el tiempo total. OpenAI usa
`OPENAI_API_KEY` y `OPENAI_IMAGE_MODEL`; xAI usa `XAI_API_KEY` y, opcionalmente,
`XAI_IMAGE_MODEL`. Los resultados se guardan en `generated_images/`. El benchmark de
xAI también guarda las tres entradas exactas con sufijos `-T`, `-S` y `-F` para debug.

### Android

Para el emulador estándar de Android:

```dotenv
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

Para un dispositivo físico conectado al servidor local sin Docker, usar la IP LAN de la computadora:

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

El deploy con Docker Compose levanta tres servicios:

- `nginx`, único servicio publicado, en los puertos `80` y `443`.
- `api`, el servidor FastAPI, accesible solamente dentro de la red de Docker en el puerto `8000`.
- `certbot`, utilizado para emitir y renovar el certificado de Let's Encrypt.

Nginx redirige HTTP a HTTPS, sirve `/images/...` directamente desde `generated_images/` y envía las demás rutas al servidor Python mediante `proxy_pass`. La carpeta se monta en ambos contenedores, con acceso de solo lectura para Nginx.

El registro DNS `A` de `sadmonkey.app` debe apuntar a la IP pública del servidor. Los puertos TCP `80` y `443` deben estar permitidos tanto en UFW como en el firewall del proveedor.

Configurar en `.env` la URL HTTPS pública:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_PROFILE=balanced
PUBLIC_BASE_URL=https://sadmonkey.app
EXPO_PUBLIC_API_URL=https://sadmonkey.app
```

### Emitir el certificado por primera vez

Arrancar temporalmente la API y Nginx en HTTP:

```bash
docker compose down
docker compose --profile bootstrap up -d --build api nginx-bootstrap
curl http://sadmonkey.app/health
```

Emitir el certificado, reemplazando el correo:

```bash
docker compose run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  --email admin@sadmonkey.app \
  --agree-tos --no-eff-email \
  -d sadmonkey.app
```

Detener el servidor temporal e iniciar Nginx con HTTPS:

```bash
docker compose stop nginx-bootstrap
docker compose rm -f nginx-bootstrap
docker compose up -d api nginx
curl https://sadmonkey.app/health
```

### Actualizar el servidor

Después de publicar cambios en el repositorio, actualizar y reconstruir los contenedores en el servidor:

```bash
cd /opt/photobook_ai
git pull
docker compose up -d --build
docker compose restart nginx
docker compose ps
docker compose logs --tail=100
curl https://sadmonkey.app/health
```

### Renovación

Probar la renovación sin modificar el certificado:

```bash
docker compose run --rm certbot renew --dry-run
```

Agregar al `crontab` de root una ejecución diaria. Nginx se recarga después para tomar un certificado renovado:

```cron
17 3 * * * cd /opt/photobook_ai && docker compose run --rm certbot renew --quiet && docker compose exec nginx nginx -s reload
```

El puerto `8000` no debe exponerse directamente a internet. El endpoint de generación no incluye autenticación propia; el proxy o la infraestructura deben aplicar límites de solicitudes y el control de acceso correspondiente.

`generated_images/` queda persistida en el host y debe tener permisos de escritura. Definir también una política de eliminación para las fotografías antiguas.

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

### Subir el APK al servidor

Desde la raíz del repositorio en la Mac, copiar el APK a la raíz del proyecto en el
servidor:

```bash
scp android/app/build/outputs/apk/release/app-release.apk root@sadmonkey.app:/opt/photobook_ai/app-release.apk
```

Comprobar que el archivo llegó correctamente:

```bash
ssh root@sadmonkey.com 'ls -lh /opt/photobook_ai/app-release.apk'
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
