import React, { useEffect, useRef } from 'react';
import { View, Text, Image, StyleSheet, ViewStyle, ImageSourcePropType, Animated } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface HazardChipProps {
  /** Hazard type identifier (e.g., "earthquake", "wildfire") */
  hazardType: string;
  /** Display label */
  label: string;
  /** Icon asset for this hazard */
  iconSource: ImageSourcePropType;
  /** Whether this hazard has an active alert */
  isActive?: boolean;
  /** Optional count or metric badge */
  badge?: string | number;
  /** Callback when chip is pressed */
  onPress?: () => void;
  /** Custom container style */
  style?: ViewStyle;
}

/**
 * Hazard Chip Component
 *
 * Compact, interactive chip representing a hazard type.
 * Used in filtering, category selection, or summary displays.
 *
 * Shows hazard icon, optional alert indicator, and optional metric badge.
 */
export function HazardChip({
  hazardType,
  label,
  iconSource,
  isActive = false,
  badge,
  onPress,
  style,
}: HazardChipProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const scale = useRef(new Animated.Value(1)).current;
  const bgAnim = useRef(new Animated.Value(isActive ? 1 : 0)).current;

  useEffect(() => {
    // Scale pulse on activation
    if (isActive) {
      Animated.sequence([
        Animated.timing(scale, { toValue: 1.08, duration: 120, useNativeDriver: true }),
        Animated.timing(scale, { toValue: 1, duration: 150, useNativeDriver: true }),
      ]).start();
    }
    // Animate background interpolation
    Animated.timing(bgAnim, {
      toValue: isActive ? 1 : 0,
      duration: 200,
      useNativeDriver: false, // backgroundColor can't use native driver
    }).start();
  }, [isActive]);

  const animatedBg = bgAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [palette.surface, palette.primary],
  });

  const animatedBorder = bgAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [palette.border, palette.primary],
  });

  const chipText = isActive ? palette.white : palette.text;

  // NOTE: transform (scale) is animated with useNativeDriver: true, while
  // backgroundColor/borderColor must use useNativeDriver: false. Mixing both
  // drivers on a single Animated.View crashes with
  // "Attempting to run JS driven animation on animated node that has been moved to native".
  // We keep them split: outer view drives scale (native), inner drives colors (JS).
  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <Animated.View
        style={[
          styles.container,
          {
            backgroundColor: animatedBg,
            borderColor: animatedBorder,
          },
          style,
        ]}
        onTouchEnd={onPress}
      >
        {/* Icon */}
        <Image
          source={iconSource}
          style={styles.icon}
          resizeMode="contain"
        />

        {/* Label */}
        <Text
          style={[
            styles.label,
            {
              color: chipText,
              fontFamily: Fonts.sans,
              fontWeight: '600',
            },
          ]}
        >
          {label}
        </Text>

        {/* Badge (if provided) */}
        {badge !== undefined && (
          <View
            style={[
              styles.badge,
              {
                backgroundColor: isActive ? palette.white : palette.danger,
              },
            ]}
          >
            <Text
              style={[
                styles.badgeText,
                {
                  color: isActive ? palette.danger : palette.white,
                  fontFamily: Fonts.sans,
                  fontWeight: '700',
                },
              ]}
            >
              {badge}
            </Text>
          </View>
        )}

        {/* Alert Indicator Dot */}
        {isActive && (
          <View
            style={[
              styles.alertIndicator,
              { backgroundColor: palette.danger },
            ]}
          />
        )}
      </Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.pill,
    borderWidth: 1,
    gap: Spacing.sm,
    position: 'relative',
  },
  icon: {
    width: 20,
    height: 20,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    lineHeight: 16,
  },
  badge: {
    minWidth: 24,
    minHeight: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: Spacing.xs,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    lineHeight: 12,
  },
  alertIndicator: {
    position: 'absolute',
    top: -4,
    right: -4,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: 'white',
  },
});
