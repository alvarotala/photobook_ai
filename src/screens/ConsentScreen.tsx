import { Image, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors } from '../theme';
import type { Scene } from '../types';

type Props = { scene: Scene; onAccept: () => void; onBack: () => void };

export function ConsentScreen({ scene, onAccept, onBack }: Props) {
  return (
    <View style={styles.container}>
      <ScreenHeader title="Antes de la foto" step="PASO 2 DE 3" onBack={onBack} />
      <View style={styles.content}>
        <Image source={scene.image} style={styles.preview} />
        <Text style={styles.title}>Prepará tu mejor pose</Text>
        <Text style={styles.scene}>{scene.title}</Text>
        <View style={styles.tipCard}>
          <Text style={styles.tipIcon}>◎</Text>
          <View style={styles.tipCopy}>
            <Text style={styles.tipTitle}>Consejo para esta escena</Text>
            <Text style={styles.tipText}>{scene.instruction}</Text>
          </View>
        </View>
      </View>
      <View style={styles.footer}>
        <PrimaryButton onPress={onAccept}>CONTINUAR</PrimaryButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { flex: 1, paddingHorizontal: 26, paddingTop: 16 },
  preview: { width: '100%', height: 230, borderRadius: 24, resizeMode: 'cover' },
  title: { color: colors.text, fontSize: 31, fontWeight: '900', textAlign: 'center', marginTop: 25 },
  scene: { color: colors.primary, fontSize: 16, fontWeight: '800', textAlign: 'center', marginTop: 5 },
  tipCard: { flexDirection: 'row', backgroundColor: colors.surfaceRaised, borderRadius: 20, padding: 20, marginTop: 26, borderWidth: 1, borderColor: colors.border },
  tipIcon: { color: colors.primary, fontSize: 33, width: 48 },
  tipCopy: { flex: 1 },
  tipTitle: { color: colors.text, fontSize: 16, fontWeight: '800' },
  tipText: { color: colors.muted, fontSize: 15, lineHeight: 22, marginTop: 5 },
  privacyCard: { padding: 19, marginTop: 16, borderLeftWidth: 3, borderLeftColor: colors.blue, backgroundColor: '#111A2A', borderRadius: 12 },
  privacyTitle: { color: colors.text, fontSize: 14, fontWeight: '800' },
  privacyText: { color: colors.muted, fontSize: 13, lineHeight: 19, marginTop: 5 },
  footer: { padding: 26, paddingBottom: 38 },
});
