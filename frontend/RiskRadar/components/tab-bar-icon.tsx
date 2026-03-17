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
