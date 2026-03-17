import { Tabs } from 'expo-router';
import React from 'react';
import { Image, StyleSheet } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors, Radius, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

const homeTabIcon = {
  // Standard (non-alert) state: green colors
  standard: require('@/assets/icons/navigation/RiskRadar_STND_HomeBttn.png'),
  // Alert state: red colors
  alert: require('@/assets/icons/navigation/RiskRadar_ALERT_HomeBttn.png'),
};

/**
 * HomeTabIcon renders the home tab icon with alert-aware coloring.
 * - When focused (active): shows alert variant (red) to emphasize active state
 * - When unfocused (inactive): shows standard variant (green)
 * 
 * In the future, this can be enhanced to show actual alert state from app context.
 */
function HomeTabIcon({ focused }: { focused: boolean }) {
  return (
    <Image
      source={focused ? homeTabIcon.alert : homeTabIcon.standard}
      style={styles.homeIcon}
      resizeMode="contain"
    />
  );
}

export default function TabLayout() {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const tabBarStyle = [
    styles.tabBar,
    { backgroundColor: palette.card, borderTopColor: palette.border },
  ];

  return (
    <Tabs
      screenOptions={{
        sceneStyle: { backgroundColor: palette.background },
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarShowLabel: true,
        tabBarActiveTintColor: palette.primary,
        tabBarInactiveTintColor: palette.textSecondary,
        tabBarActiveBackgroundColor: palette.secondary,
        tabBarStyle,
        tabBarItemStyle: styles.tabBarItem,
        tabBarLabelStyle: styles.tabBarLabel,
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ focused }) => <HomeTabIcon focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Alerts',
          tabBarIcon: ({ color }) => <IconSymbol size={24} name="bell.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    height: 86,
    borderTopWidth: 1,
    paddingTop: Spacing.sm,
    paddingBottom: Spacing.md,
    paddingHorizontal: Spacing.md,
  },
  tabBarItem: {
    marginHorizontal: Spacing.xs,
    borderRadius: Radius.button,
  },
  tabBarLabel: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: '600',
    paddingBottom: 2,
  },
  homeIcon: {
    width: 30,
    height: 30,
  },
});
