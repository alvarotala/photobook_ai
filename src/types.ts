import type { ImageSourcePropType } from 'react-native';

export type AppStep = 'home' | 'scenes' | 'consent' | 'camera' | 'processing' | 'result';

export type SceneId = 'car' | 'podium' | 'hero';

export type Scene = {
  id: SceneId;
  title: string;
  eyebrow: string;
  description: string;
  instruction: string;
  image: ImageSourcePropType;
  prompt: string;
};
