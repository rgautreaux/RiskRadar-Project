import React from 'react';
import { View, Text, Image, StyleSheet, ViewStyle, ImageSourcePropType } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface RiskCardProps {
  /** Risk type key (e.g., "weather", "air-quality") */
  riskType: string;
  /** Display title for the risk */
  title: string;
  /** Risk severity level */
  severity: 'low' | 'moderate' | 'high' | 'critical';
  /** Icon asset for this hazard type */
  iconSource: ImageSourcePropType;
  /** Risk description or details */
  description?: string;
  /** Current risk value/metric */
  value?: string | number;
  /** Unit of measurement */
  unit?: string;
  /** Callback when card is pressed */
  onPress?: () => void;
  /** Custom container style */
  style?: ViewStyle;
  /** SD4: Freshness meta/timestamp string */
  meta?: string;
}

/**
 * Risk Card Component
 *
 * Displays a single risk/hazard item with icon, title, severity indicator, and details.
 * Used in grid or list layouts on Home and Alerts screens.
 *
 * Severity colors:
 * - low: Green
 * - moderate: Yellow
 * - high: Orange
 * - critical: Red
 */
export function RiskCard({
  riskType,
  title,
  severity,
  iconSource,
  description,
  value,
  unit,
  onPress,
  style,
  meta,
}: RiskCardProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const severityColors = {
    low: palette.success,
    moderate: palette.warning,
    high: '#F97316',
    critical: palette.danger,
  };

  const severityBgColors = {
    low: palette.success + '20',
    moderate: palette.warning + '20',
    high: '#F9731620',
    critical: palette.danger + '20',
  };

  return (
    <View
      style={[
        styles.outerContainer,
        style,
      ]}
      onTouchEnd={onPress}
    >
      {/* SD5: Severity Rail */}
      <View style={[styles.severityRail, { backgroundColor: severityColors[severity] }]} />
      <View
        style={[
          styles.container,
          { backgroundColor: palette.card, borderColor: palette.border },
        ]}
      >
        {/* Header with Icon and Severity */}
        <View style={styles.header}>
          <Image
            source={iconSource}
            style={styles.icon}
            resizeMode="contain"
          />
          <View
            style={[
              styles.severityBadge,
              { backgroundColor: severityBgColors[severity] },
            ]}
          >
            <Text
              style={[
                styles.severityText,
                { color: severityColors[severity] },
              ]}
            >
              {severity.charAt(0).toUpperCase() + severity.slice(1)}
            </Text>
          </View>
        </View>

        {/* Title */}
        <Text
          style={[
            styles.title,
            {
              color: palette.text,
              fontFamily: Fonts.sans,
              fontWeight: '700',
            },
          ]}
        >
          {title}
        </Text>

        {/* SD4: Freshness Meta Pattern */}
        {meta && (
          <Text
            style={{
              color: palette.textSecondary,
              fontFamily: Fonts.sans,
              fontWeight: '500',
              fontSize: 12,
              marginBottom: 2,
            }}
          >
            {meta}
          </Text>
        )}

        {/* Description */}
        {description && (
          <Text
            style={[
              styles.description,
              {
                color: palette.textSecondary,
                fontFamily: Fonts.sans,
                fontWeight: '400',
              },
            ]}
          >
            {description}
          </Text>
        )}

        {/* Value/Metric (if provided) */}
        {value !== undefined && (
          <View style={styles.metricSection}>
            <Text
              style={[
                styles.value,
                {
                  color: palette.text,
                  fontFamily: Fonts.sans,
                  fontWeight: '700',
                },
              ]}
            >
              {value}
            </Text>
            {unit && (
              <Text
                style={[
                  styles.unit,
                  {
                    color: palette.textSecondary,
                    fontFamily: Fonts.sans,
                    fontWeight: '400',
                  },
                ]}
              >
                {unit}
              </Text>
            )}
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outerContainer: {
    flexDirection: 'row',
    alignItems: 'stretch',
  },
  severityRail: {
    width: 6,
    borderTopLeftRadius: Radius.md,
    borderBottomLeftRadius: Radius.md,
    marginRight: Spacing.sm,
  },
  container: {
    flex: 1,
    borderWidth: 1,
    borderRadius: Radius.md,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.sm,
  },
  icon: {
    width: 40,
    height: 40,
  },
  severityBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.sm,
  },
  severityText: {
    fontSize: 12,
    fontWeight: '600',
    lineHeight: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    lineHeight: 20,
  },
  description: {
    fontSize: 13,
    fontWeight: '400',
    lineHeight: 18,
  },
  metricSection: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: Spacing.xs,
  },
  value: {
    fontSize: 18,
    fontWeight: '700',
    lineHeight: 24,
  },
  unit: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    marginLeft: Spacing.xs,
  },
});
