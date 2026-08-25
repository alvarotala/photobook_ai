import type { Scene } from '../types';

export const scenes: Scene[] = [
  {
    id: 'car',
    eyebrow: 'ADRENALINA',
    title: 'Dentro del auto',
    description: 'Viví la largada desde el asiento del copiloto.',
    instruction: 'Mirá al frente y sonreí como si estuvieras por largar.',
    image: require('../../templates/car.png'),
    prompt:
      'Integrate the photographed participant as the rally co-driver in the reference scene. Preserve their identity and facial features. Match the existing realistic lighting, perspective, racing suit, helmet, shadows, and camera angle.',
  },
  {
    id: 'podium',
    eyebrow: 'VICTORIA',
    title: 'En el podio',
    description: 'Celebrá una victoria inolvidable como protagonista absoluto.',
    instruction: 'Levantá un brazo o celebrá mirando de frente.',
    image: require('../../templates/podium.png'),
    prompt:
      'Integrate the photographed participant as the only winner on the podium, raising the championship trophy. Preserve their identity and facial features. Match the realistic racing suit, full-body victory pose, dramatic sunset lighting, perspective, shadows, and scale.',
  },
  {
    id: 'hero',
    eyebrow: 'LEYENDA',
    title: 'Hero pose',
    description: 'Convertite en protagonista de una escena cinematográfica.',
    instruction: 'Mantené una expresión segura y mirá directamente a cámara.',
    image: require('../../templates/hero.png'),
    prompt:
      'Integrate the photographed participant as the foreground rally driver in the reference scene. Preserve their identity and facial features. Match the realistic racing suit, cinematic golden-hour lighting, scale, shadows, perspective, and depth of field.',
  },
];
