import { Image, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';
import type { Scene } from '../types';

type Props = {
  scene: Scene;
  capturedPhotoUri: string;
  onRetake: () => void;
  onRestart: () => void;
};

export function ResultScreen({ scene, capturedPhotoUri, onRetake, onRestart }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.heading}>
        <Text style={styles.kicker}>RESULTADO DE DESARROLLO</Text>
        <Text style={styles.title}>¡Tu momento llegó!</Text>
        <Text style={styles.subtitle}>La integración con OpenAI reemplazará esta vista previa.</Text>
      </View>
      <View style={styles.resultCard}>
        <Image source={scene.image} style={styles.resultImage} />
        <View style={styles.previewBadge}><Text style={styles.previewBadgeText}>PLANTILLA · {scene.title.toUpperCase()}</Text></View>
      </View>
      <View style={styles.captureRow}>
        <Image source={{ uri: capturedPhotoUri }} style={styles.captureThumb} />
        <View style={styles.captureCopy}>
          <Text style={styles.captureTitle}>Tu captura está lista</Text>
          <Text style={styles.captureText}>Se enviará junto con la plantilla cuando configuremos la API.</Text>
        </View>
      </View>
      <View style={styles.qrPlaceholder}>
        <Text style={styles.qrIcon}>⌁</Text>
        <View style={styles.qrCopy}>
          <Text style={styles.qrTitle}>Entrega por QR pendiente</Text>
          <Text style={styles.qrText}>OpenAI devuelve la imagen, pero no una URL pública para el teléfono.</Text>
        </View>
      </View>
      <View style={styles.actions}>
        <PrimaryButton variant="secondary" onPress={onRetake}>REPETIR FOTO</PrimaryButton>
        <PrimaryButton onPress={onRestart}>FINALIZAR</PrimaryButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: 24, paddingTop: 40 },
  heading: { alignItems: 'center' },
  kicker: { color: colors.primary, fontSize: 11, fontWeight: '900', letterSpacing: 1.8 },
  title: { color: colors.text, fontSize: 34, fontWeight: '900', marginTop: 8 },
  subtitle: { color: colors.muted, fontSize: 14, textAlign: 'center', marginTop: 7 },
  resultCard: { height: 310, borderRadius: 24, overflow: 'hidden', marginTop: 24, backgroundColor: colors.surface },
  resultImage: { width: '100%', height: '100%', resizeMode: 'cover' },
  previewBadge: { position: 'absolute', left: 14, bottom: 14, backgroundColor: 'rgba(5,7,11,0.78)', borderRadius: 10, paddingVertical: 8, paddingHorizontal: 11 },
  previewBadgeText: { color: colors.text, fontSize: 10, fontWeight: '900', letterSpacing: 0.8 },
  captureRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, borderRadius: 18, padding: 14, marginTop: 16 },
  captureThumb: { width: 64, height: 64, borderRadius: 13 },
  captureCopy: { flex: 1, marginLeft: 14 },
  captureTitle: { color: colors.text, fontSize: 15, fontWeight: '800' },
  captureText: { color: colors.muted, fontSize: 12, lineHeight: 17, marginTop: 3 },
  qrPlaceholder: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#111A2A', borderRadius: 18, padding: 16, marginTop: 14, borderWidth: 1, borderColor: '#273B5F' },
  qrIcon: { width: 48, color: colors.blue, fontSize: 34, fontWeight: '900' },
  qrCopy: { flex: 1 },
  qrTitle: { color: colors.text, fontSize: 14, fontWeight: '800' },
  qrText: { color: colors.muted, fontSize: 12, lineHeight: 17, marginTop: 3 },
  actions: { marginTop: 'auto', gap: 12, paddingTop: 18 },
});
