import React, { useEffect, useRef } from 'react';
import { Animated, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors } from '@/constants/theme';
import { EASE_OUT_EXPO, EASE_OUT_QUART } from '@/components/motion/animations';

type Palette = typeof Colors.light;

/**
 * Animated temperature range bar — shows low→high span within a normalized 0..1 track.
 *
 * The fill grows outward from `startFraction` as `progress` animates 0→1,
 * giving a layered reveal after the row itself slides in. When used on the "Today"
 * row, pass `todayMarker` (0..1) to draw a small dot at the current high-temp position.
 *
 * Width/left use `useNativeDriver: false` because they animate layout; the marker
 * opacity uses the native driver.
 */
export function TempBar({
  startFraction,
  endFraction,
  delay = 0,
  palette,
  reducedMotion = false,
  todayMarker,
}: {
  startFraction: number; // 0..1, normalized low position
  endFraction: number;   // 0..1, normalized high position
  delay?: number;
  palette: Palette;
  reducedMotion?: boolean;
  todayMarker?: number;  // 0..1, optional dot position
}) {
  const progress = useRef(new Animated.Value(reducedMotion ? 1 : 0)).current;
  const markerOpacity = useRef(new Animated.Value(reducedMotion ? 1 : 0)).current;

  useEffect(() => {
    if (reducedMotion) {
      progress.setValue(1);
      markerOpacity.setValue(1);
      return;
    }
    const timer = setTimeout(() => {
      Animated.timing(progress, {
        toValue: 1,
        duration: 600,
        easing: EASE_OUT_EXPO,
        useNativeDriver: false, // width + left animations
      }).start();
      Animated.timing(markerOpacity, {
        toValue: 1,
        duration: 320,
        delay: 280,
        easing: EASE_OUT_QUART,
        useNativeDriver: true,
      }).start();
    }, delay);
    return () => clearTimeout(timer);
  }, [delay, reducedMotion, progress, markerOpacity]);

  // Bar expands from startFraction outward. At progress=0, it's a zero-width line at startFraction.
  // At progress=1, it spans startFraction..endFraction.
  const span = Math.max(0, endFraction - startFraction);
  const widthInterp = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', `${span * 100}%`],
  });

  return (
    <View style={{ flex: 1, height: 6, backgroundColor: palette.surfaceMuted, borderRadius: 3, maxWidth: 120, overflow: 'hidden', position: 'relative' }}>
      <Animated.View
        style={{
          position: 'absolute',
          top: 0,
          left: `${startFraction * 100}%`,
          height: 6,
          width: widthInterp,
          borderRadius: 3,
          overflow: 'hidden',
        }}
      >
        <LinearGradient
          colors={[palette.primary, palette.success]}
          start={{ x: 0, y: 0.5 }}
          end={{ x: 1, y: 0.5 }}
          style={{ flex: 1, borderRadius: 3 }}
        />
      </Animated.View>
      {typeof todayMarker === 'number' && (
        <Animated.View
          style={{
            position: 'absolute',
            top: -1,
            left: `${todayMarker * 100}%`,
            width: 8,
            height: 8,
            borderRadius: 4,
            backgroundColor: palette.white,
            borderWidth: 1.5,
            borderColor: palette.primary,
            marginLeft: -4, // center the dot on the marker position
            opacity: markerOpacity,
          }}
        />
      )}
    </View>
  );
}
