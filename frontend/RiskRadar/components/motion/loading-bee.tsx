import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';

type Palette = typeof Colors.light;

/**
 * LoadingBee — calm, premium loading affordance for the AI summary card.
 *
 * Why this exists: the generic `ActivityIndicator` + "Loading..." text looked
 * broken during longer LLM calls (3–10s). Users would be tempted to restart
 * the app. A deliberate, gently-moving bee signals "the system is working on
 * it" without the alarm of a frantic spinner.
 *
 * Motion design (per `.impeccable.md`: calm over alarm, minimal, slick):
 *  - A single shared `t` value (0→1, looping 2.6s) drives the flight path.
 *  - translateX/Y are 90° out of phase, producing a smooth oval.
 *  - rotate tilts ±6° toward the direction of motion — like a real insect.
 *  - The label pulses opacity 0.5↔1.0 on a 1.8s sine cycle, independent of flight.
 *  - Everything uses native-driver transforms (GPU-accelerated).
 *  - `reducedMotion` renders a static bee with full-opacity label — content
 *    is still communicated, motion is simply removed.
 */
export function LoadingBee({
  label = 'Loading your briefing\u2026',
  reducedMotion = false,
  palette,
}: {
  label?: string;
  reducedMotion?: boolean;
  palette: Palette;
}) {
  // 0→1 loop that shapes the flight path via keyframed interpolations.
  const t = useRef(new Animated.Value(0)).current;
  // 0↔1 sequence for label opacity pulse.
  const textPulse = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (reducedMotion) return;

    const flight = Animated.loop(
      Animated.timing(t, {
        toValue: 1,
        duration: 2600,
        easing: Easing.linear,
        useNativeDriver: true,
      }),
    );
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(textPulse, {
          toValue: 0.5,
          duration: 900,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(textPulse, {
          toValue: 1,
          duration: 900,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ]),
    );
    flight.start();
    pulse.start();
    return () => {
      flight.stop();
      pulse.stop();
    };
  }, [reducedMotion, t, textPulse]);

  if (reducedMotion) {
    return (
      <View style={styles.container} accessible accessibilityLabel={`${label}. Please wait.`}>
        <MaterialCommunityIcons name="bee" size={44} color={palette.warning} />
        <Text style={[styles.label, { color: palette.textSecondary }]}>{label}</Text>
      </View>
    );
  }

  // Keyframed oval flight path. Seamless loop because frame 0 == frame 1.
  const translateX = t.interpolate({
    inputRange: [0, 0.25, 0.5, 0.75, 1],
    outputRange: [-24, 0, 24, 0, -24],
  });
  const translateY = t.interpolate({
    inputRange: [0, 0.25, 0.5, 0.75, 1],
    outputRange: [0, -8, 0, 8, 0],
  });
  const rotate = t.interpolate({
    inputRange: [0, 0.25, 0.5, 0.75, 1],
    outputRange: ['-6deg', '0deg', '6deg', '0deg', '-6deg'],
  });

  return (
    <View style={styles.container} accessible accessibilityLabel={`${label}. Please wait.`}>
      <Animated.View
        style={{
          transform: [{ translateX }, { translateY }, { rotate }],
        }}
      >
        <MaterialCommunityIcons name="bee" size={44} color={palette.warning} />
      </Animated.View>
      <Animated.Text
        style={[
          styles.label,
          { color: palette.textSecondary, opacity: textPulse },
        ]}
      >
        {label}
      </Animated.Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 28,
    gap: 16,
    minHeight: 140,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    letterSpacing: 0.2,
  },
});
