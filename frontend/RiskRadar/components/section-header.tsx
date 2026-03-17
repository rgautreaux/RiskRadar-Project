import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface SectionHeaderProps {
  /** Section title text */
  title: string;
  /** Optional subtitle text */
  subtitle?: string;
  /** Optional action button text */
  actionLabel?: string;
  /** Callback when action button is pressed */
  onActionPress?: () => void;
  /** Custom container style */
  style?: ViewStyle;
  /** Custom title style */
  titleStyle?: TextStyle;
}

/**
 * Section Header Component
 *
 * Displays a branded section header with title, optional subtitle, and optional action button.
 * Used to separate major content sections (e.g., "Your Alerts", "Recent Risks").
 *
 * Coordinates with the RiskRadar_DataHeader_Format.png asset reference.
 */
export function SectionHeader({
  title,
  subtitle,
  actionLabel,
  onActionPress,
  style,
  titleStyle,
}: SectionHeaderProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: palette.background },
        style,
      ]}
    >
      <View style={styles.textSection}>
        <Text
          style={[
            styles.title,
            {
              color: palette.text,
              fontFamily: Fonts.sans,
              fontSize: 18,
              fontWeight: '700',
            },
            titleStyle,
          ]}
        >
          {title}
        </Text>
        {subtitle && (
          <Text
            style={[
              styles.subtitle,
              {
                color: palette.textSecondary,
                fontFamily: Fonts.sans,
                fontSize: 14,
                fontWeight: '400',
              },
            ]}
          >
            {subtitle}
          </Text>
        )}
      </View>

      {actionLabel && (
        <View
          style={[styles.actionButton, { backgroundColor: palette.primary }]}
          onTouchEnd={onActionPress}
        >
          <Text
            style={[
              styles.actionLabel,
              {
                color: palette.white,
                fontFamily: Fonts.sans,
                fontWeight: '600',
              },
            ]}
          >
            {actionLabel}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  textSection: {
    flex: 1,
  },
  title: {
    fontWeight: '700',
    lineHeight: 24,
  },
  subtitle: {
    fontWeight: '400',
    lineHeight: 20,
    marginTop: Spacing.xs,
  },
  actionButton: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.button,
    marginLeft: Spacing.md,
  },
  actionLabel: {
    fontSize: 12,
    fontWeight: '600',
    lineHeight: 16,
  },
});
