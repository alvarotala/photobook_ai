import { FlatList, ImageBackground, Pressable, StyleSheet, Text, View } from 'react-native';

import { ScreenHeader } from '../components/ScreenHeader';
import { scenes } from '../data/scenes';
import { colors } from '../theme';
import type { Scene } from '../types';

type Props = { onBack: () => void; onSelect: (scene: Scene) => void };

export function SceneSelectionScreen({ onBack, onSelect }: Props) {
  return (
    <View style={styles.container}>
      <ScreenHeader title="Elegí tu escena" step="PASO 1 DE 3" onBack={onBack} />
      <Text style={styles.lead}>¿Dónde querés vivir tu momento de rally?</Text>
      <FlatList
        contentContainerStyle={styles.list}
        data={scenes}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <Pressable
            accessibilityRole="button"
            onPress={() => onSelect(item)}
            style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
          >
            <ImageBackground source={item.image} style={styles.image} imageStyle={styles.imageRadius}>
              <View style={styles.cardScrim} />
              <View style={styles.number}><Text style={styles.numberText}>0{index + 1}</Text></View>
              <View style={styles.cardContent}>
                <Text style={styles.eyebrow}>{item.eyebrow}</Text>
                <Text style={styles.cardTitle}>{item.title}</Text>
                <Text style={styles.description}>{item.description}</Text>
              </View>
              <View style={styles.arrow}><Text style={styles.arrowText}>→</Text></View>
            </ImageBackground>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  lead: { color: colors.muted, textAlign: 'center', fontSize: 16, marginTop: 8, marginBottom: 10 },
  list: { padding: 22, paddingBottom: 36, gap: 18 },
  card: { height: 220, borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: colors.border },
  cardPressed: { transform: [{ scale: 0.985 }], opacity: 0.85 },
  image: { flex: 1, justifyContent: 'flex-end' },
  imageRadius: { borderRadius: 23 },
  cardScrim: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(5,7,11,0.35)' },
  number: { position: 'absolute', top: 16, left: 16, backgroundColor: colors.primary, borderRadius: 12, paddingHorizontal: 12, paddingVertical: 7 },
  numberText: { color: colors.text, fontWeight: '900', fontSize: 13 },
  cardContent: { padding: 20, paddingRight: 74 },
  eyebrow: { color: '#FFB09B', fontSize: 11, fontWeight: '900', letterSpacing: 1.6 },
  cardTitle: { color: colors.text, fontSize: 29, fontWeight: '900', marginTop: 4 },
  description: { color: '#E1E4EA', fontSize: 15, marginTop: 5 },
  arrow: { position: 'absolute', right: 18, bottom: 20, width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(255,255,255,0.16)', alignItems: 'center', justifyContent: 'center' },
  arrowText: { color: colors.text, fontSize: 26, fontWeight: '700' },
});
