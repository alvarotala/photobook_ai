FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server/requirements.txt server/requirements.txt
RUN python -m pip install --no-cache-dir -r server/requirements.txt

COPY server server
COPY templates templates

RUN mkdir -p /app/generated_images

EXPOSE 8000

CMD ["python", "-m", "server"]
