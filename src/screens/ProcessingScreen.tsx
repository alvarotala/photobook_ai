import { useEffect, useState } from 'react';
import { ActivityIndicator, ImageBackground, StyleSheet, Text, View } from 'react-native';

import { colors } from '../theme';
import type { Scene } from '../types';

const messages = [
  'Preparando tu escena',
  'Ajustando iluminación y perspectiva',
  'Integrándote en el mundo del rally',
  'Aplicando el acabado cinematográfico',
];

type Props = { scene: Scene; onComplete: () => void };

export function ProcessingScreen({ scene, onComplete }: Props) {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const messageTimer = setInterval(() => setMessageIndex((value) => Math.min(value + 1, messages.length - 1)), 1400);
    const finishTimer = setTimeout(onComplete, 5_600);
    return () => { clearInterval(messageTimer); clearTimeout(finishTimer); };
  }, [onComplete]);

  return (
    <ImageBackground source={scene.image} style={styles.container} blurRadius={18}>
      <View style={styles.scrim} />
      <View style={styles.content}>
        <View style={styles.spinner}><ActivityIndicator color={colors.primary} size="large" /></View>
        <Text style={styles.kicker}>LA MAGIA ESTÁ OCURRIENDO</Text>
        <Text style={styles.title}>Creando tu{`\n`}momento épico</Text>
        <Text style={styles.message}>{messages[messageIndex]}…</Text>
        <View style={styles.progress}><View style={[styles.progressFill, { width: `${25 * (messageIndex + 1)}%` }]} /></View>
        <Text style={styles.note}>No cierres la experiencia</Text>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrim: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(5,7,11,0.8)' },
  content: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  spinner: { width: 100, height: 100, borderRadius: 50, backgroundColor: colors.surfaceRaised, alignItems: 'center', justifyContent: 'center', marginBottom: 34 },
  kicker: { color: colors.primary, fontSize: 12, fontWeight: '900', letterSpacing: 2 },
  title: { color: colors.text, fontSize: 43, lineHeight: 47, fontWeight: '900', textAlign: 'center', marginTop: 14 },
  message: { color: '#DADDE4', fontSize: 17, marginTop: 28, minHeight: 26, textAlign: 'center' },
  progress: { width: '78%', height: 8, borderRadius: 4, backgroundColor: colors.surfaceRaised, overflow: 'hidden', marginTop: 24 },
  progressFill: { height: '100%', backgroundColor: colors.primary, borderRadius: 4 },
  note: { color: colors.muted, fontSize: 13, marginTop: 16 },
});
