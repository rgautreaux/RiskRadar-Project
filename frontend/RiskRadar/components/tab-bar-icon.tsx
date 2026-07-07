import React from 'react';
import { Image, StyleSheet, ImageSourcePropType, ViewStyle } from 'react-native';

export interface TabBarIconProps {
  /** Source for the active/focused icon */
  sourceFocused: ImageSourcePropType;
  /** Source for the inactive/unfocused icon */
  sourceUnfocused: ImageSourcePropType;
  /** Whether the tab is currently focused */
  focused: boolean;
  /** Size of the icon in pixels */
  size?: number;
  /** Custom style for the image */
  style?: ViewStyle;
}

/**
 * Tab Bar Icon Component
 *
 * Renders appropriate icon (active or inactive) for tab navigation.
 * Handles switching between focused and unfocused visual states.
 *
 * Used in conjunction with Tabs navigation configuration for consistent
 * icon presentation across the bottom tab bar.
 */
export function TabBarIcon({
  sourceFocused,
  sourceUnfocused,
  focused,
  size = 30,
  style,
}: TabBarIconProps) {
  // SD10: Tab Bar Ownership Detail
  // Mapping rationale: When the tab is focused (active), use the branded PNG asset for the focused state (e.g., green for Home, red for Alerts) as per wireframe intent.
  // When unfocused, use the standard PNG asset for the inactive state. This ensures the tab bar always reflects RiskRadar's brand color logic and matches the design system.
  const iconSource = focused ? sourceFocused : sourceUnfocused;

  return (
    <Image
      source={iconSource}
      style={[
        styles.icon,
        {
          width: size,
          height: size,
        },
        style,
      ]}
      resizeMode="contain"
    />
  );
}

const styles = StyleSheet.create({
  icon: {
    // Base filtering/rendering applied uniformly
  },
});
