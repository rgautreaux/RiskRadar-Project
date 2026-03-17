import React from 'react';
import { View, ViewProps, StyleSheet, ViewStyle } from 'react-native';

import { Colors, Shadows, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export type ThemedViewProps = ViewProps & {
  /**
   * Semantic surface token to apply as background.
   * - 'background': full-screen background color
   * - 'card': elevated card/surface color (typically white in light mode)
   * - 'surfaceMuted': muted/secondary surface color
   * @default 'background'
   */
  surface?: 'background' | 'card' | 'surfaceMuted';
  /**
   * Whether to apply a card shadow (elevation).
   * @default false
   */
  elevated?: boolean;
  /**
   * Padding preset for the container. If omitted, no automatic padding is applied.
   * Use StyleSheet manually for custom padding.
   * @default undefined
   */
  padding?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
};

export function ThemedView({
  style,
  surface = 'background',
  elevated = false,
  padding,
  ...rest
}: ThemedViewProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  // Resolve background color based on surface semantic
  let backgroundColor: string;
  switch (surface) {
    case 'card':
      backgroundColor = palette.card;
      break;
    case 'surfaceMuted':
      backgroundColor = palette.surfaceMuted;
      break;
    case 'background':
    default:
      backgroundColor = palette.background;
      break;
  }

  // Build style array
  const viewStyle: ViewProps['style'] = [
    { backgroundColor },
    padding && getPaddingStyle(padding),
    elevated && Shadows.card,
    style,
  ];

  return (
    <View
      style={viewStyle}
      {...rest}
    />
  );
}

/**
 * Resolve padding values from preset keys.
 */
function getPaddingStyle(
  padding: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
): ViewStyle {
  const paddingMap = {
    xs: Spacing.xs,
    sm: Spacing.sm,
    md: Spacing.md,
    lg: Spacing.lg,
    xl: Spacing.xl,
  };

  return {
    padding: paddingMap[padding],
  };
}

const styles = StyleSheet.create({
  default: {
    flex: 0,
  },
});
