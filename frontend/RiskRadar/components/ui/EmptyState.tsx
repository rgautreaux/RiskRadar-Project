import React from 'react';
import { View, Text, StyleSheet, Image, ViewStyle, TextStyle } from 'react-native';
import { Colors, Spacing, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

const radarIcon = require('@/assets/icons/navigation/RiskRadar_STND_Logo.png');

export interface EmptyStateProps {
  title: string;
  subtitle?: string;
  style?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
}

export function EmptyState({ title, subtitle, style, titleStyle, subtitleStyle }: EmptyStateProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  return (
    <View style={[styles.container, style]}>
      <Image source={radarIcon} style={styles.icon} resizeMode="contain" />
      <Text style={[styles.title, { color: palette.text }, titleStyle]}>{title}</Text>
      {subtitle && <Text style={[styles.subtitle, { color: palette.textSecondary }, subtitleStyle]}>{subtitle}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.xl,
  },
  icon: {
    width: 48,
    height: 48,
    marginBottom: Spacing.md,
  },
  title: {
    fontFamily: Fonts.sans,
    fontWeight: '700',
    fontSize: 18,
    marginBottom: Spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontFamily: Fonts.sans,
    fontWeight: '400',
    fontSize: 14,
    textAlign: 'center',
  },
});

export default EmptyState;
