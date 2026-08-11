import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors } from '../theme';

type Props = {
  title: string;
  step?: string;
  onBack?: () => void;
};

export function ScreenHeader({ title, step, onBack }: Props) {
  return (
    <View style={styles.header}>
      <View style={styles.side}>
        {onBack && (
          <Pressable accessibilityLabel="Volver" onPress={onBack} style={styles.backButton}>
            <Text style={styles.backIcon}>‹</Text>
          </Pressable>
        )}
      </View>
      <View style={styles.center}>
        {step && <Text style={styles.step}>{step}</Text>}
        <Text style={styles.title}>{title}</Text>
      </View>
      <View style={styles.side} />
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    minHeight: 82,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  side: { width: 58 },
  center: { flex: 1, alignItems: 'center' },
  backButton: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceRaised,
  },
  backIcon: { color: colors.text, fontSize: 42, lineHeight: 44, marginTop: -5 },
  step: { color: colors.primary, fontSize: 12, fontWeight: '900', letterSpacing: 1.5 },
  title: { color: colors.text, fontSize: 20, fontWeight: '800', marginTop: 3 },
});
