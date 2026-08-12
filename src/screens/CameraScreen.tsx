import { CameraView, useCameraPermissions } from 'expo-camera';
import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';
import type { Scene } from '../types';

type Props = { scene: Scene; onCapture: (uri: string) => void; onBack: () => void };

export function CameraScreen({ scene, onCapture, onBack }: Props) {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [countdown, setCountdown] = useState<number | null>(null);
  const [capturing, setCapturing] = useState(false);

  useEffect(() => {
    if (countdown === null) return;
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown((value) => (value ?? 1) - 1), 900);
      return () => clearTimeout(timer);
    }

    const capture = async () => {
      try {
        setCapturing(true);
        const photo = await cameraRef.current?.takePictureAsync({ skipProcessing: true });
        if (photo?.uri) onCapture(photo.uri);
      } finally {
        setCountdown(null);
        setCapturing(false);
      }
    };
    void capture();
  }, [countdown, onCapture]);

  if (!permission) {
    return <View style={styles.center}><ActivityIndicator color={colors.primary} size="large" /></View>;
  }

  if (!permission.granted) {
    return (
      <View style={styles.permission}>
        <Text style={styles.permissionTitle}>Necesitamos acceso a la cámara</Text>
        <Text style={styles.permissionText}>La cámara se usa solamente para crear tu composición.</Text>
        <PrimaryButton onPress={() => void requestPermission()}>HABILITAR CÁMARA</PrimaryButton>
        <PrimaryButton variant="ghost" onPress={onBack}>VOLVER</PrimaryButton>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="front" mirror />
      <View style={styles.shadeTop} />
      <View style={styles.header}>
        <Pressable onPress={onBack} style={styles.back}><Text style={styles.backText}>‹</Text></Pressable>
        <View style={styles.copy}>
          <Text style={styles.step}>PASO 3 DE 3</Text>
          <Text style={styles.title}>Mirá a cámara</Text>
        </View>
        <View style={styles.back} />
      </View>
      <View style={styles.guideWrap}>
        <View style={styles.faceGuide} />
        <Text style={styles.instruction}>{scene.instruction}</Text>
      </View>
      <View style={styles.footer}>
        <Pressable
          accessibilityLabel="Tomar fotografía"
          disabled={capturing || countdown !== null}
          onPress={() => setCountdown(3)}
          style={styles.shutterOuter}
        >
          <View style={styles.shutterInner} />
        </Pressable>
        <Text style={styles.footerHint}>Tocá para iniciar la cuenta regresiva</Text>
      </View>
      {countdown !== null && <View style={styles.countdownOverlay}><Text style={styles.countdown}>{countdown || '¡Listo!'}</Text></View>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' },
  permission: { flex: 1, backgroundColor: colors.background, justifyContent: 'center', padding: 32, gap: 18 },
  permissionTitle: { color: colors.text, fontSize: 32, fontWeight: '900', textAlign: 'center' },
  permissionText: { color: colors.muted, fontSize: 17, lineHeight: 25, textAlign: 'center', marginBottom: 20 },
  shadeTop: { position: 'absolute', left: 0, right: 0, top: 0, height: 170, backgroundColor: 'rgba(0,0,0,0.42)' },
  header: { height: 105, paddingTop: 22, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center' },
  back: { width: 54, height: 54, borderRadius: 16, backgroundColor: 'rgba(0,0,0,0.45)', alignItems: 'center', justifyContent: 'center' },
  backText: { color: colors.text, fontSize: 42, lineHeight: 44, marginTop: -5 },
  copy: { flex: 1, alignItems: 'center' },
  step: { color: '#FFB09B', fontSize: 12, fontWeight: '900', letterSpacing: 1.4 },
  title: { color: colors.text, fontSize: 23, fontWeight: '900', marginTop: 4 },
  guideWrap: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  faceGuide: { width: 280, height: 370, borderRadius: 150, borderWidth: 4, borderColor: 'rgba(255,255,255,0.9)', borderStyle: 'dashed' },
  instruction: { color: colors.text, fontSize: 16, fontWeight: '700', textAlign: 'center', backgroundColor: 'rgba(0,0,0,0.55)', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 999, marginTop: 24, maxWidth: '86%' },
  footer: { height: 180, backgroundColor: 'rgba(5,7,11,0.72)', alignItems: 'center', justifyContent: 'center' },
  shutterOuter: { width: 88, height: 88, borderRadius: 44, borderWidth: 5, borderColor: colors.text, alignItems: 'center', justifyContent: 'center' },
  shutterInner: { width: 66, height: 66, borderRadius: 33, backgroundColor: colors.primary },
  footerHint: { color: colors.muted, fontSize: 13, marginTop: 12 },
  countdownOverlay: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(0,0,0,0.38)', alignItems: 'center', justifyContent: 'center' },
  countdown: { color: colors.text, fontSize: 130, fontWeight: '900', textShadowColor: colors.primary, textShadowRadius: 28 },
});
