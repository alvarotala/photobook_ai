import { API_URL } from '../config';
import type { GeneratedImage, SceneId } from '../types';

type GenerateParams = {
  photoUri: string;
  scene: SceneId;
  signal?: AbortSignal;
};

type GenerateResponse = {
  id: string;
  image_url: string;
};

function filenameFromUri(uri: string): string {
  const candidate = uri.split('/').pop()?.split('?')[0];
  return candidate && candidate.includes('.') ? candidate : 'participant.jpg';
}

function contentTypeFromFilename(filename: string): string {
  const extension = filename.split('.').pop()?.toLowerCase();
  if (extension === 'png') return 'image/png';
  if (extension === 'webp') return 'image/webp';
  return 'image/jpeg';
}

export async function generatePhotobookImage({
  photoUri,
  scene,
  signal,
}: GenerateParams): Promise<GeneratedImage> {
  const filename = filenameFromUri(photoUri);
  const form = new FormData();
  form.append('scene', scene);
  form.append(
    'photo',
    {
      uri: photoUri,
      name: filename,
      type: contentTypeFromFilename(filename),
    } as unknown as Blob,
  );

  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      body: form,
      signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') throw error;
    throw new Error(`No se pudo conectar con el servidor en ${API_URL}`);
  }

  if (!response.ok) {
    let detail = `El servidor respondió ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) detail = payload.detail;
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(detail);
  }

  const payload = (await response.json()) as GenerateResponse;
  if (!payload.id || !payload.image_url) {
    throw new Error('El servidor devolvió una respuesta incompleta');
  }
  return { id: payload.id, imageUrl: payload.image_url };
}
