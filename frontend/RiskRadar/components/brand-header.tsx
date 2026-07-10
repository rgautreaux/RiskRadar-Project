import React from 'react';
import { View, Image, StyleSheet, ViewStyle, Text } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface BrandHeaderProps {
  /** Whether to show alert state (red) or standard state (blue) */
  isAlert?: boolean;
  /** Callback when notification icon is pressed */
  onNotificationPress?: () => void;
  /** Custom container style */
  style?: ViewStyle;
  /** Scope: 'local' or 'global' */
  scope?: 'local' | 'global';
  /** Show the scope (Local/Global) chip on the right */
  showScope?: boolean;
  /** Show the notification bell button on the right */
  showNotification?: boolean;
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
  scope = 'local',
  showScope = true,
  showNotification = true,
}: BrandHeaderProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const logoSource = isAlert
    ? require('@/assets/icons/branding/RiskRadar_ALERT_Logo.png')
    : require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

  const notifIconSource = isAlert
    ? require('@/assets/icons/navigation/RiskRadar_ALERT_NotifIcon.png')
    : require('@/assets/icons/navigation/RiskRadar_STND_NotifIcon.png');

  // SD2: Scope chip assets
  const scopeIcon = scope === 'local'
    ? require('@/assets/icons/navigation/RiskRadar_Local_Icon.png')
    : require('@/assets/icons/navigation/RiskRadar_GEN_Global_Icon.png');
  const scopeLabel = scope === 'local' ? 'Local' : 'Global';

  return (
    <View style={[styles.container, { backgroundColor: palette.primaryDark }, style]}>
      <View style={styles.logoSection}>
        <Image
          source={logoSource}
          style={styles.logo}
          resizeMode="contain"
        />
        <Text style={[styles.wordmark, { color: palette.white, fontFamily: Fonts.sans }]}>
          RiskRadar
        </Text>
      </View>

      {(showScope || showNotification) && (
        <View style={styles.rightSection}>
          {showScope && (
            <View style={[styles.scopeIndicator, { backgroundColor: palette.surface }]}>
              <Image source={scopeIcon} style={styles.scopeIcon} resizeMode="contain" />
              <View style={{ width: 4 }} />
              <Text style={{ color: palette.text, fontFamily: Fonts.sans, fontWeight: '600', fontSize: 13 }}>
                {scopeLabel}
              </Text>
            </View>
          )}

          {showNotification && (
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
          )}
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
    paddingTop: Spacing.md,
    paddingBottom: Spacing.md,
  },
  logoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  logo: {
    width: 36,
    height: 36,
    marginRight: Spacing.sm,
  },
  wordmark: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
   scopeIndicator: {
     flexDirection: 'row',
     alignItems: 'center',
     paddingHorizontal: Spacing.md,
     paddingVertical: Spacing.sm,
     borderRadius: Radius.sm,
     minWidth: 80,
   },
  scopeIcon: {
    width: 18,
    height: 18,
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
