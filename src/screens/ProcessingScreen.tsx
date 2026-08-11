import { useEffect, useState } from 'react';
import { ActivityIndicator, ImageBackground, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { generatePhotobookImage } from '../services/photobookApi';
import { colors } from '../theme';
import type { GeneratedImage, Scene } from '../types';

const messages = [
  'Preparando tu escena',
  'Ajustando iluminación y perspectiva',
  'Integrándote en el mundo del rally',
  'Aplicando el acabado cinematográfico',
];

type Props = {
  scene: Scene;
  photoUri: string;
  onComplete: (result: GeneratedImage) => void;
  onBack: () => void;
};

export function ProcessingScreen({ scene, photoUri, onComplete, onBack }: Props) {
  const [messageIndex, setMessageIndex] = useState(0);
  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setError(null);
    setMessageIndex(0);

    const messageTimer = setInterval(
      () => setMessageIndex((value) => (value + 1) % messages.length),
      2_800,
    );

    generatePhotobookImage({ photoUri, scene: scene.id, signal: controller.signal })
      .then(onComplete)
      .catch((reason: unknown) => {
        if (reason instanceof Error && reason.name === 'AbortError') return;
        setError(reason instanceof Error ? reason.message : 'No pudimos crear la imagen');
      })
      .finally(() => clearInterval(messageTimer));

    return () => {
      controller.abort();
      clearInterval(messageTimer);
    };
  }, [attempt, onComplete, photoUri, scene.id]);

  return (
    <ImageBackground source={scene.image} style={styles.container} blurRadius={18}>
      <View style={styles.scrim} />
      <View style={styles.content}>
        {error ? (
          <>
            <View style={styles.errorIcon}><Text style={styles.errorMark}>!</Text></View>
            <Text style={styles.kicker}>ALGO NO SALIÓ BIEN</Text>
            <Text style={styles.errorTitle}>No pudimos crear tu imagen</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <View style={styles.actions}>
              <PrimaryButton onPress={() => setAttempt((value) => value + 1)}>REINTENTAR</PrimaryButton>
              <PrimaryButton variant="secondary" onPress={onBack}>REPETIR FOTO</PrimaryButton>
            </View>
          </>
        ) : (
          <>
            <View style={styles.spinner}><ActivityIndicator color={colors.primary} size="large" /></View>
            <Text style={styles.kicker}>LA MAGIA ESTÁ OCURRIENDO</Text>
            <Text style={styles.title}>Creando tu{`\n`}momento épico</Text>
            <Text style={styles.message}>{messages[messageIndex]}…</Text>
            <View style={styles.progress}><View style={styles.progressFill} /></View>
            <Text style={styles.note}>Este proceso puede tardar hasta un par de minutos</Text>
          </>
        )}
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrim: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(5,7,11,0.82)' },
  content: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  spinner: { width: 100, height: 100, borderRadius: 50, backgroundColor: colors.surfaceRaised, alignItems: 'center', justifyContent: 'center', marginBottom: 34 },
  kicker: { color: colors.primary, fontSize: 12, fontWeight: '900', letterSpacing: 2, textAlign: 'center' },
  title: { color: colors.text, fontSize: 43, lineHeight: 47, fontWeight: '900', textAlign: 'center', marginTop: 14 },
  message: { color: '#DADDE4', fontSize: 17, marginTop: 28, minHeight: 26, textAlign: 'center' },
  progress: { width: '78%', height: 8, borderRadius: 4, backgroundColor: colors.surfaceRaised, overflow: 'hidden', marginTop: 24 },
  progressFill: { height: '100%', width: '42%', backgroundColor: colors.primary, borderRadius: 4 },
  note: { color: colors.muted, fontSize: 13, marginTop: 16, textAlign: 'center' },
  errorIcon: { width: 88, height: 88, borderRadius: 44, backgroundColor: '#3B171B', alignItems: 'center', justifyContent: 'center', marginBottom: 28 },
  errorMark: { color: colors.danger, fontSize: 48, fontWeight: '900' },
  errorTitle: { color: colors.text, fontSize: 34, lineHeight: 39, fontWeight: '900', textAlign: 'center', marginTop: 14 },
  errorMessage: { color: colors.muted, fontSize: 16, lineHeight: 23, textAlign: 'center', marginTop: 18 },
  actions: { alignSelf: 'stretch', gap: 12, marginTop: 34 },
});
