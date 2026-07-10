import React, { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Text, ViewStyle } from 'react-native';

/**
 * Shared easing curves.
 * Use `EASE_OUT_QUART` for most UI entrances — natural, refined deceleration.
 * Use `EASE_OUT_EXPO` for faster, more decisive settles (e.g. count-ups, bar fills).
 *
 * Avoid bounce/elastic curves — they feel dated and draw attention to the animation
 * rather than the content.
 */
export const EASE_OUT_QUART = Easing.bezier(0.25, 1, 0.5, 1);
export const EASE_OUT_EXPO = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * FadeInView — entrance animation: fade + subtle vertical slide.
 *
 * Renders children with opacity 0 → 1 and `translateY: distance → 0` running in parallel.
 * When `reducedMotion` is true, the animation is skipped and children appear instantly
 * at their final state.
 *
 * Use this as the default entrance wrapper across the dashboard for a calm, cohesive
 * choreography. Pass incrementing `delay` values to stagger siblings.
 */
export function FadeInView({
  delay = 0,
  duration = 450,
  distance = 18,
  children,
  style,
  reducedMotion = false,
}: {
  delay?: number;
  duration?: number;
  distance?: number;
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
  reducedMotion?: boolean;
}) {
  const opacity = useRef(new Animated.Value(reducedMotion ? 1 : 0)).current;
  const translateY = useRef(new Animated.Value(reducedMotion ? 0 : distance)).current;

  useEffect(() => {
    if (reducedMotion) return;
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, {
          toValue: 1, duration, easing: EASE_OUT_QUART, useNativeDriver: true,
        }),
        Animated.timing(translateY, {
          toValue: 0, duration, easing: EASE_OUT_QUART, useNativeDriver: true,
        }),
      ]).start();
    }, delay);
    return () => clearTimeout(timer);
  }, [delay, duration, reducedMotion, opacity, translateY]);

  return (
    <Animated.View style={[style, { opacity, transform: [{ translateY }] }]}>
      {children}
    </Animated.View>
  );
}

/**
 * HeroRise — subtle scale-in from 0.98 → 1 that runs alongside an inner FadeInView
 * for a layered "settling into place" feel on the weather hero.
 */
export function HeroRise({
  children,
  reducedMotion,
}: {
  children: React.ReactNode;
  reducedMotion: boolean;
}) {
  const scale = useRef(new Animated.Value(reducedMotion ? 1 : 0.98)).current;
  useEffect(() => {
    if (reducedMotion) return;
    Animated.timing(scale, {
      toValue: 1,
      duration: 520,
      delay: 80,
      easing: EASE_OUT_QUART,
      useNativeDriver: true,
    }).start();
  }, [reducedMotion, scale]);
  return <Animated.View style={{ transform: [{ scale }] }}>{children}</Animated.View>;
}

/**
 * CountUp — animates a number counting up from 0 to its target value.
 *
 * Uses ease-out-expo for a confident, decisive settle. When `reducedMotion` is true
 * the final value is shown immediately. Rendered as a `<Text>` node with the suffix
 * appended (e.g. `suffix="°"` for temperatures).
 */
export function CountUp({
  to,
  duration = 700,
  suffix = '',
  style,
  reducedMotion = false,
}: {
  to: number;
  duration?: number;
  suffix?: string;
  style?: any;
  reducedMotion?: boolean;
}) {
  const [value, setValue] = useState(reducedMotion ? to : 0);

  useEffect(() => {
    if (reducedMotion) {
      setValue(to);
      return;
    }
    const startVal = 0;
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const t = Math.min(1, elapsed / duration);
      // ease-out-expo
      const eased = 1 - Math.pow(2, -10 * t);
      const current = Math.round(startVal + (to - startVal) * eased);
      setValue(current);
      if (t < 1) {
        requestAnimationFrame(tick);
      } else {
        setValue(to);
      }
    };
    const raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to, duration, reducedMotion]);

  return <Text style={style}>{value}{suffix}</Text>;
}
