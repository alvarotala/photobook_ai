import { Image, StyleSheet, Text, View } from 'react-native';
import QRCode from 'react-native-qrcode-svg';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';
import type { GeneratedImage, Scene } from '../types';

type Props = {
  scene: Scene;
  capturedPhotoUri: string;
  generatedImage: GeneratedImage;
  onRetake: () => void;
  onRestart: () => void;
};

export function ResultScreen({
  scene,
  capturedPhotoUri,
  generatedImage,
  onRetake,
  onRestart,
}: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.heading}>
        <Text style={styles.kicker}>IMAGEN LISTA</Text>
        <Text style={styles.title}>¡Tu momento llegó!</Text>
        <Text style={styles.subtitle}>{scene.title}</Text>
      </View>
      <View style={styles.resultCard}>
        <Image source={{ uri: generatedImage.imageUrl }} style={styles.resultImage} resizeMode="cover" />
      </View>
      <View style={styles.deliveryCard}>
        <View style={styles.qrBox}>
          <QRCode value={generatedImage.imageUrl} size={126} backgroundColor="#FFFFFF" color="#090B10" />
        </View>
        <View style={styles.deliveryCopy}>
          <Text style={styles.deliveryTitle}>Escaneá para descargar</Text>
          <Text style={styles.deliveryText}>Abrí la cámara de tu teléfono y apuntá al código QR.</Text>
          <Text numberOfLines={1} style={styles.imageId}>ID {generatedImage.id}</Text>
        </View>
      </View>
      <View style={styles.captureRow}>
        <Image source={{ uri: capturedPhotoUri }} style={styles.captureThumb} />
        <Text style={styles.captureText}>Tu foto original se usó únicamente para crear esta composición.</Text>
      </View>
      <View style={styles.actions}>
        <PrimaryButton variant="secondary" onPress={onRetake}>REPETIR FOTO</PrimaryButton>
        <PrimaryButton onPress={onRestart}>FINALIZAR</PrimaryButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: 24, paddingTop: 34 },
  heading: { alignItems: 'center' },
  kicker: { color: colors.success, fontSize: 11, fontWeight: '900', letterSpacing: 1.8 },
  title: { color: colors.text, fontSize: 34, fontWeight: '900', marginTop: 7 },
  subtitle: { color: colors.primary, fontSize: 14, fontWeight: '800', marginTop: 4 },
  resultCard: { height: 300, borderRadius: 24, overflow: 'hidden', marginTop: 19, backgroundColor: colors.surface },
  resultImage: { width: '100%', height: '100%' },
  deliveryCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, borderRadius: 20, padding: 15, marginTop: 15, borderWidth: 1, borderColor: colors.border },
  qrBox: { padding: 8, borderRadius: 12, backgroundColor: '#FFFFFF' },
  deliveryCopy: { flex: 1, marginLeft: 17 },
  deliveryTitle: { color: colors.text, fontSize: 19, fontWeight: '900' },
  deliveryText: { color: colors.muted, fontSize: 13, lineHeight: 19, marginTop: 6 },
  imageId: { color: colors.blue, fontSize: 10, fontWeight: '800', marginTop: 10 },
  captureRow: { flexDirection: 'row', alignItems: 'center', marginTop: 13, paddingHorizontal: 4 },
  captureThumb: { width: 46, height: 46, borderRadius: 10 },
  captureText: { flex: 1, color: colors.muted, fontSize: 11, lineHeight: 16, marginLeft: 12 },
  actions: { marginTop: 'auto', gap: 10, paddingTop: 14 },
});
