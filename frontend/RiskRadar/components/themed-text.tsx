import React from 'react';
import { Text, TextProps, StyleSheet } from 'react-native';

import { Colors, Fonts, Typography } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export type ThemedTextProps = TextProps & {
  /**
   * Text variant tied to typography tokens for consistent scaling.
   * @default 'body'
   */
  type?:
    | 'hero' // Screen hero titles: large, bold, rounded serif
    | 'title' // Section titles: large, bold, sans
    | 'subtitle' // Section subtitles: semibold, sans
    | 'sectionTitle' // Section headers: semibold, rounded
    | 'cardTitle' // Card headings: semibold, sans
    | 'eyebrow' // Overline/metadata: semibold, all-caps
    | 'body' // Body text: regular, sans
    | 'meta'; // Metadata/caption: medium, sans
  /**
   * Semantic color role: text primary, secondary, or custom color.
   * @default 'primary'
   */
  lightColor?: string;
  darkColor?: string;
};

export function ThemedText({
  style,
  type = 'body',
  lightColor,
  darkColor,
  ...rest
}: ThemedTextProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  // Default colors based on scheme
  const color = scheme === 'light' ? (lightColor || palette.text) : (darkColor || palette.text);

  // Retrieve typography style for variant
  const typographyStyle = getTypographyStyle(type);

  return (
    <Text
      style={[
        { color },
        typographyStyle,
        style,
      ]}
      {...rest}
    />
  );
}

/**
 * Retrieve the typography style object for a given variant.
 */
function getTypographyStyle(
  type: ThemedTextProps['type'],
): React.CSSProperties {
  const fontFamily =
    Fonts.sans || 'system-ui, -apple-system, BlinkMacSystemFont, Segoe UI';

  switch (type) {
    case 'hero':
      return {
        ...Typography.hero,
        fontFamily: Fonts.rounded,
      };
    case 'title':
      return {
        ...Typography.title,
        fontFamily: Fonts.sans,
      };
    case 'subtitle':
      return {
        ...Typography.subtitle,
        fontFamily: Fonts.sans,
      };
    case 'sectionTitle':
      return {
        ...Typography.sectionLabel,
        fontFamily: Fonts.rounded,
      };
    case 'cardTitle':
      return {
        ...Typography.cardHeading,
        fontFamily: Fonts.sans,
      };
    case 'eyebrow':
      return {
        fontFamily: Fonts.sans,
        fontSize: 10,
        lineHeight: 14,
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
      };
    case 'body':
      return {
        ...Typography.body,
        fontFamily: Fonts.sans,
      };
    case 'meta':
      return {
        ...Typography.meta,
        fontFamily: Fonts.sans,
      };
    default:
      return {
        ...Typography.body,
        fontFamily: Fonts.sans,
      };
  }
}

const styles = StyleSheet.create({
  default: {
    textAlign: 'left',
  },
});
