import React, { useEffect, useRef } from 'react';
import { Animated, ScrollView, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { EASE_OUT_QUART } from '@/components/motion/animations';
import { weatherIcon } from '@/components/weather/weather-icon';

type Palette = typeof Colors.light;

/**
 * Minimal shape required from a forecast day to synthesize hourly slots.
 * Accepts any object that happens to have these three fields (structural typing),
 * so callers can pass the full `ForecastDay` interface from `app/(tabs)/index.tsx`
 * without us having to share a types module.
 */
interface ForecastShape {
  high_temp: number;
  low_temp: number;
  weather_main: string;
}

/** One slot in the hourly forecast strip. */
export interface HourlySlot {
  label: string;      // "Now", "2 PM", "12 AM", etc.
  hour: number;       // 0..23 (hour of day for this slot)
  temp: number;       // rounded °F
  weatherMain: string;
  isNow: boolean;
}

/**
 * Synthesize an 8-slot hourly forecast from the current day's high/low.
 *
 * We don't have a true hourly feed from the backend — we approximate the daily
 * temperature curve using a sine wave that peaks around 3 PM and troughs around
 * 5 AM. Always surface this as estimated to the user (see the "Estimated from
 * daily range" subheader on the dashboard's hourly card).
 *
 * Slots: Now, +2h, +4h, +6h, +8h, +12h, +16h, +24h.
 * Slots that cross midnight use tomorrow's high/low if provided.
 */
export function synthesizeHourlyForecast(today: ForecastShape, tomorrow?: ForecastShape): HourlySlot[] {
  const now = new Date();
  const currentHour = now.getHours();
  const offsets = [0, 2, 4, 6, 8, 12, 16, 24];

  const todayAvg = (today.high_temp + today.low_temp) / 2;
  const todayAmp = (today.high_temp - today.low_temp) / 2;
  const tomorrowAvg = tomorrow ? (tomorrow.high_temp + tomorrow.low_temp) / 2 : todayAvg;
  const tomorrowAmp = tomorrow ? (tomorrow.high_temp - tomorrow.low_temp) / 2 : todayAmp;

  // sin peaks at hour 15 (3 PM), troughs around hour 3 (just before dawn)
  // temp(h) = avg + amp * sin((h - 9) * π / 12)
  const tempAtHour = (absoluteHour: number, avg: number, amp: number): number => {
    const h = ((absoluteHour % 24) + 24) % 24;
    return avg + amp * Math.sin(((h - 9) * Math.PI) / 12);
  };

  return offsets.map((offset, i) => {
    const targetHour = currentHour + offset;
    const dayIndex = Math.floor(targetHour / 24);
    const hourOfDay = ((targetHour % 24) + 24) % 24;
    const useTomorrow = dayIndex >= 1 && !!tomorrow;
    const avg = useTomorrow ? tomorrowAvg : todayAvg;
    const amp = useTomorrow ? tomorrowAmp : todayAmp;
    const temp = tempAtHour(targetHour, avg, amp);

    let label: string;
    if (i === 0) {
      label = 'Now';
    } else if (hourOfDay === 0) {
      label = '12 AM';
    } else if (hourOfDay === 12) {
      label = '12 PM';
    } else if (hourOfDay < 12) {
      label = `${hourOfDay} AM`;
    } else {
      label = `${hourOfDay - 12} PM`;
    }

    return {
      label,
      hour: hourOfDay,
      temp: Math.round(temp),
      weatherMain: useTomorrow && tomorrow ? tomorrow.weather_main : today.weather_main,
      isNow: i === 0,
    };
  });
}

/**
 * Horizontal hourly forecast row — iOS-Weather-inspired: time / icon / temp per slot.
 *
 * Slots fade + slide in from the right with a 40ms stagger, starting at `baseDelay`.
 * Honors `reducedMotion` by rendering everything instantly at its final state.
 */
export function HourlyForecastRow({
  slots,
  palette,
  baseDelay,
  reducedMotion,
}: {
  slots: HourlySlot[];
  palette: Palette;
  baseDelay: number;
  reducedMotion: boolean;
}) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={{ paddingHorizontal: 16, paddingVertical: 14, gap: 6 }}
    >
      {slots.map((slot, i) => (
        <HourlySlotCell
          key={`${slot.label}-${i}`}
          slot={slot}
          palette={palette}
          delay={baseDelay + i * 40}
          reducedMotion={reducedMotion}
        />
      ))}
    </ScrollView>
  );
}

/**
 * Individual hourly slot cell. Internal to this module — exported only through
 * HourlyForecastRow. The "Now" slot uses a bolder weight and the primary color
 * to separate it from the estimated future slots.
 */
function HourlySlotCell({
  slot,
  palette,
  delay,
  reducedMotion,
}: {
  slot: HourlySlot;
  palette: Palette;
  delay: number;
  reducedMotion: boolean;
}) {
  const opacity = useRef(new Animated.Value(reducedMotion ? 1 : 0)).current;
  const translateX = useRef(new Animated.Value(reducedMotion ? 0 : 10)).current;

  useEffect(() => {
    if (reducedMotion) return;
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 360, easing: EASE_OUT_QUART, useNativeDriver: true }),
        Animated.timing(translateX, { toValue: 0, duration: 360, easing: EASE_OUT_QUART, useNativeDriver: true }),
      ]).start();
    }, delay);
    return () => clearTimeout(timer);
  }, [delay, reducedMotion, opacity, translateX]);

  return (
    <Animated.View
      accessible
      accessibilityLabel={`${slot.label}, ${slot.temp} degrees, ${slot.weatherMain.toLowerCase()}`}
      style={{
        opacity,
        transform: [{ translateX }],
        width: 60,
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingVertical: 8,
        gap: 10,
      }}
    >
      <Text
        style={{
          fontSize: 13,
          fontWeight: slot.isNow ? '700' : '500',
          color: slot.isNow ? palette.text : palette.textSecondary,
          letterSpacing: 0.2,
        }}
      >
        {slot.label}
      </Text>
      <Ionicons
        name={weatherIcon(slot.weatherMain)}
        size={22}
        color={slot.isNow ? palette.primary : palette.text}
      />
      <Text
        style={{
          fontSize: 17,
          fontWeight: slot.isNow ? '700' : '600',
          color: slot.isNow ? palette.primary : palette.text,
        }}
      >
        {slot.temp}°
      </Text>
    </Animated.View>
  );
}
