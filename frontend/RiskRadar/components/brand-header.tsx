import React from 'react';
import { View, Image, StyleSheet, ViewStyle } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface BrandHeaderProps {
  /** Whether to show alert state (red) or standard state (blue) */
  isAlert?: boolean;
  /** Callback when notification icon is pressed */
  onNotificationPress?: () => void;
  /** Custom container style */
  style?: ViewStyle;
}

/**
 * Brand Header Component
 *
 * Displays the RiskRadar branded header with logo, branding text, and notification button.
 * Adapts to alert state (red) or standard state (blue).
 *
 * Used on main app screens for consistent header presentation.
 */
export function BrandHeader({
  isAlert = false,
  onNotificationPress,
  style,
}: BrandHeaderProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const logoSource = isAlert
    ? require('@/assets/icons/branding/RiskRadar_ALERT_Logo.png')
    : require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

  const brandTextSource = isAlert
    ? require('@/assets/icons/branding/RiskRadar_ALERT_Text.png')
    : require('@/assets/icons/branding/RiskRadar_STND_Text.png');

  const notifIconSource = isAlert
    ? require('@/assets/icons/navigation/RiskRadar_ALERT_NotifIcon.png')
    : require('@/assets/icons/navigation/RiskRadar_STND_NotifIcon.png');

  return (
    <View style={[styles.container, { backgroundColor: palette.primaryDark }, style]}>
      <View style={styles.logoSection}>
        <Image
          source={logoSource}
          style={styles.logo}
          resizeMode="contain"
        />
        <Image
          source={brandTextSource}
          style={styles.brandText}
          resizeMode="contain"
        />
      </View>

      <View style={styles.rightSection}>
        {/* Location/Scope Indicator Placeholder */}
        <View style={[styles.scopeIndicator, { backgroundColor: palette.surface }]}>
          {/* TODO: Add scope icon and text */}
        </View>

        {/* Notification Button */}
        <View
          style={[styles.notificationButton, { backgroundColor: palette.surface }]}
          onTouchEnd={onNotificationPress}
        >
          <Image
            source={notifIconSource}
            style={styles.notificationIcon}
            resizeMode="contain"
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.md,
  },
  logoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  logo: {
    width: 40,
    height: 40,
    marginRight: Spacing.sm,
  },
  brandText: {
    height: 24,
    flex: 1,
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  scopeIndicator: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.sm,
    minWidth: 80,
    alignItems: 'center',
  },
  notificationButton: {
    width: 40,
    height: 40,
    borderRadius: Radius.button,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationIcon: {
    width: 24,
    height: 24,
  },
});
