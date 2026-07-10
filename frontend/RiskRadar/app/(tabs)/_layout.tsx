import { Tabs } from 'expo-router';
import React from 'react';
import { Image, ImageSourcePropType, StyleSheet } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { Colors, Radius, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

const TAB_ICONS = {
  home: require('@/assets/icons/navigation/RiskRadar_STND_HomeBttn.png') as ImageSourcePropType,
  alerts: require('@/assets/icons/navigation/RiskRadar_ALERT_HomeBttn.png') as ImageSourcePropType,
  saved: require('@/assets/icons/navigation/RiskRadar_DEST_Global_Icon.png') as ImageSourcePropType,
};

/** TabIcon renders a branded PNG icon with subtle focus opacity. */
function TabIcon({ source, focused }: { source: ImageSourcePropType; focused: boolean }) {
  return (
    <Image
      source={source}
      style={[styles.tabIcon, { opacity: focused ? 1 : 0.55 }]}
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
          tabBarIcon: ({ focused }) => <TabIcon source={TAB_ICONS.home} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Alerts',
          tabBarIcon: ({ focused }) => <TabIcon source={TAB_ICONS.alerts} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="saved"
        options={{
          title: 'Saved',
          tabBarIcon: ({ focused }) => <TabIcon source={TAB_ICONS.saved} focused={focused} />,
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
  tabIcon: {
    width: 28,
    height: 28,
  },
});
