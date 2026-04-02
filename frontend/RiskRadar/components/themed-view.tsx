import React from 'react';
import { View, StyleProp, ViewProps, ViewStyle } from 'react-native';

import { Colors, Shadows, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export type ThemedViewProps = ViewProps & {
  surface?: 'background' | 'card' | 'surfaceMuted';
  elevated?: boolean;
  padding?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  style?: StyleProp<ViewStyle>;
};

export function ThemedView(props: ThemedViewProps) {
  const {
    style,
    surface = 'background',
    elevated = false,
    padding,
    ...rest
  } = props;

  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

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

  const viewStyle: StyleProp<ViewStyle> = [
    { backgroundColor },
    padding ? getPaddingStyle(padding) : null,
    elevated ? Shadows.card : null,
    style,
  ];

  return <View style={viewStyle} {...rest} />;
}

function getPaddingStyle(padding: NonNullable<ThemedViewProps['padding']>): ViewStyle {
  const paddingMap = {
    xs: Spacing.xs,
    sm: Spacing.sm,
    md: Spacing.md,
    lg: Spacing.lg,
    xl: Spacing.xl,
  } as const;

  return {
    padding: paddingMap[padding],
  };
}
