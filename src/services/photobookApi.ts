import { fetch } from 'expo/fetch';
import { File } from 'expo-file-system';

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

export async function generatePhotobookImage({
  photoUri,
  scene,
  signal,
}: GenerateParams): Promise<GeneratedImage> {
  const photo = new File(photoUri);
  if (!photo.exists) {
    throw new Error('La fotografía capturada ya no está disponible en el dispositivo');
  }

  const form = new FormData();
  form.append('scene', scene);
  form.append('photo', photo, photo.name || 'participant.jpg');

  let response;
  try {
    response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      body: form,
      signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') throw error;
    const reason = error instanceof Error && error.message ? `: ${error.message}` : '';
    throw new Error(`No se pudo conectar con el servidor en ${API_URL}${reason}`);
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
