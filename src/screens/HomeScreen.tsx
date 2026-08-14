import { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Image, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';

type Props = { onStart: () => void };

const BACKGROUNDS = [
  require('../../images/backgrounds/01.jpg'),
  require('../../images/backgrounds/02.jpg'),
  require('../../images/backgrounds/03.jpg'),
  require('../../images/backgrounds/04.jpg'),
  require('../../images/backgrounds/05.jpg'),
  require('../../images/backgrounds/06.jpg'),
];

const BACKGROUND_HOLD_MS = 10_500;
const BACKGROUND_FADE_MS = 2_800;

export function HomeScreen({ onStart }: Props) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [nextIndex, setNextIndex] = useState<number | null>(null);
  const currentIndexRef = useRef(0);
  const isTransitioning = useRef(false);
  const pan = useRef(new Animated.Value(-20)).current;
  const fade = useRef(new Animated.Value(0)).current;
  const pulse = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const panAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(pan, {
          toValue: 20,
          duration: 14_000,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(pan, {
          toValue: -20,
          duration: 14_000,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ]),
    );

    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, {
          toValue: 1,
          duration: 1_600,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(pulse, {
          toValue: 0,
          duration: 1_600,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ]),
    );

    panAnimation.start();
    pulseAnimation.start();

    const backgroundTimer = setInterval(() => {
      if (isTransitioning.current) return;

      isTransitioning.current = true;
      const upcomingIndex = (currentIndexRef.current + 1) % BACKGROUNDS.length;
      setNextIndex(upcomingIndex);

      Animated.timing(fade, {
        toValue: 1,
        duration: BACKGROUND_FADE_MS,
        easing: Easing.inOut(Easing.quad),
        useNativeDriver: true,
      }).start(({ finished }) => {
        if (!finished) return;
        currentIndexRef.current = upcomingIndex;
        setCurrentIndex(upcomingIndex);
        setNextIndex(null);
        fade.setValue(0);
        isTransitioning.current = false;
      });
    }, BACKGROUND_HOLD_MS);

    return () => {
      clearInterval(backgroundTimer);
      panAnimation.stop();
      pulseAnimation.stop();
      fade.stopAnimation();
    };
  }, [fade, pan, pulse]);

  const backgroundMotion = {
    transform: [{ translateX: pan }, { scale: 1.06 }],
  };
  const glowOpacity = pulse.interpolate({ inputRange: [0, 1], outputRange: [0.18, 0.55] });
  const glowScale = pulse.interpolate({ inputRange: [0, 1], outputRange: [0.98, 1.08] });
  const buttonScale = pulse.interpolate({ inputRange: [0, 1], outputRange: [1, 1.012] });

  return (
    <View style={styles.container}>
      <Animated.Image
        source={BACKGROUNDS[currentIndex]}
        style={[styles.background, backgroundMotion]}
        resizeMode="cover"
      />
      {nextIndex !== null && (
        <Animated.Image
          source={BACKGROUNDS[nextIndex]}
          style={[styles.background, backgroundMotion, { opacity: fade }]}
          resizeMode="cover"
        />
      )}

      <View style={styles.scrim} />

      <View style={styles.sponsorBar} accessibilityLabel="Itaipú, Yacyretá y Gobierno del Paraguay">
        <View style={styles.itaipuLogoFrame}>
          <Image
            source={require('../../images/logos/itaipu.png')}
            style={styles.itaipuLogo}
            resizeMode="contain"
            accessibilityLabel="Itaipú"
          />
        </View>
        <View style={styles.logoDivider} />
        <Image
          source={require('../../images/logos/yasyreta.png')}
          style={styles.yasyretaLogo}
          resizeMode="contain"
          accessibilityLabel="Entidad Binacional Yacyretá"
        />
        <View style={styles.logoDivider} />
        <Image
          source={require('../../images/logos/gdp.png')}
          style={styles.governmentLogo}
          resizeMode="contain"
          accessibilityLabel="Gobierno del Paraguay"
        />
      </View>

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
        <Animated.View style={[styles.buttonWrap, { transform: [{ scale: buttonScale }] }]}>
          <Animated.View
            pointerEvents="none"
            style={[styles.buttonGlow, { opacity: glowOpacity, transform: [{ scale: glowScale }] }]}
          />
          <PrimaryButton onPress={onStart}>COMENZAR EXPERIENCIA  →</PrimaryButton>
        </Animated.View>
        <Text style={styles.hint}>Tocá la pantalla para comenzar</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'flex-end', overflow: 'hidden' },
  background: {
    ...StyleSheet.absoluteFill,
    left: '-6%',
    width: '112%',
    height: '100%',
  },
  scrim: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(5, 7, 11, 0.55)',
  },
  sponsorBar: {
    position: 'absolute',
    marginHorizontal: 14,
    top: 34,
    alignSelf: 'center',
    height: 68,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 18,
    paddingVertical: 0,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.92)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.65)',
  },
  governmentLogo: { width: 148, height: 34 },
  itaipuLogoFrame: { width: 78, height: 62, overflow: 'hidden', alignItems: 'center' },
  itaipuLogo: { width: 130, height: 62 },
  yasyretaLogo: { width: 83, height: 56 },
  logoDivider: {
    width: 1,
    height: 32,
    marginHorizontal: 14,
    backgroundColor: 'rgba(9,11,16,0.14)',
  },
  topBadge: {
    position: 'absolute',
    top: 122,
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(9,11,16,0.78)',
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
  buttonGlow: {
    ...StyleSheet.absoluteFill,
    borderRadius: 24,
    backgroundColor: colors.primary,
  },
  hint: { color: colors.muted, textAlign: 'center', marginTop: 16, fontSize: 13 },
});
