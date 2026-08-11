import { ImageBackground, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';

type Props = { onStart: () => void };

export function HomeScreen({ onStart }: Props) {
  return (
    <ImageBackground source={require('../../templates/hero.png')} style={styles.container} resizeMode="cover">
      <View style={styles.scrim} />
      <View style={styles.topBadge}>
        <View style={styles.dot} />
        <Text style={styles.badgeText}>EXPERIENCIA RALLY AI</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.kicker}>TU MOMENTO. TU HISTORIA.</Text>
        <Text style={styles.title}>Entrá al mundo{`\n`}del rally</Text>
        <Text style={styles.subtitle}>
          Elegí una escena, sacate una foto y dejá que la inteligencia artificial haga el resto.
        </Text>
        <View style={styles.buttonWrap}>
          <PrimaryButton onPress={onStart}>COMENZAR EXPERIENCIA  →</PrimaryButton>
        </View>
        <Text style={styles.hint}>Tocá la pantalla para comenzar</Text>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'flex-end' },
  scrim: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(5, 7, 11, 0.6)',
  },
  topBadge: {
    position: 'absolute',
    top: 46,
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(9,11,16,0.8)',
    borderColor: 'rgba(255,255,255,0.16)',
    borderWidth: 1,
    borderRadius: 999,
    paddingVertical: 11,
    paddingHorizontal: 18,
  },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.primary, marginRight: 9 },
  badgeText: { color: colors.text, fontWeight: '800', fontSize: 12, letterSpacing: 1.4 },
  content: { paddingHorizontal: 30, paddingBottom: 72 },
  kicker: { color: colors.primary, fontSize: 14, fontWeight: '900', letterSpacing: 2.2 },
  title: { color: colors.text, fontSize: 54, lineHeight: 56, fontWeight: '900', marginTop: 14 },
  subtitle: { color: '#D8DCE4', fontSize: 19, lineHeight: 28, marginTop: 20, maxWidth: 560 },
  buttonWrap: { marginTop: 34 },
  hint: { color: colors.muted, textAlign: 'center', marginTop: 16, fontSize: 13 },
});
