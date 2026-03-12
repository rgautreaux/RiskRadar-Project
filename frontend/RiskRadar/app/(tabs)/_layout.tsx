import { Tabs } from 'expo-router';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import React from 'react';
import { Image, StyleSheet } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { Colors, Radius, Spacing } from '@/constants/theme';

const homeTabIcon = {
  inactive: require('@/assets/icons/navigation/RiskRadar_STND_HomeBttn.png'),
  active: require('@/assets/icons/navigation/RiskRadar_ALERT_HomeBttn.png'),
};

function HomeTabIcon({ focused }: { focused: boolean }) {
  return (
    <Image
      source={focused ? homeTabIcon.active : homeTabIcon.inactive}
      style={styles.homeIcon}
      resizeMode="contain"
    />
  );
}

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        sceneStyle: { backgroundColor: Colors.light.background },
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarShowLabel: true,
        tabBarActiveTintColor: Colors.light.primary,
        tabBarInactiveTintColor: Colors.light.textSecondary,
        tabBarActiveBackgroundColor: Colors.light.secondary,
        tabBarStyle: styles.tabBar,
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
          tabBarIcon: ({ color, focused }) => (
            <MaterialIcons
              size={24}
              name={focused ? 'notifications-active' : 'notifications-none'}
              color={color}
            />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    height: 86,
    backgroundColor: Colors.light.white,
    borderTopColor: Colors.light.border,
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
