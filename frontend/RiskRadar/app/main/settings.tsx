import React, { useState } from 'react';
import {
  View,
  Text,
  Switch,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
  TextInput,
  Alert,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import * as Notifications from 'expo-notifications';
import { Colors, Spacing, Radius, Shadows, Typography, SafeArea } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { PrimaryButton } from '@/components/ui/PrimaryButton';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

export default function SettingsScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  
  const { user, isLoggedIn, logout, isDevUserMode, toggleDevUserMode } = useAuth();

  const [pushEnabled, setPushEnabled] = useState(false);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [useGps, setUseGps] = useState(false);
  const [zipCode, setZipCode] = useState(user?.zip_code || '');

  const handlePushToggle = async (value: boolean) => {
    if (!value) {
      setPushEnabled(false);
      if (isLoggedIn && user) {
        apiFetch(`/users/${user.id}/preferences`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ device_token: null }),
        }).catch(() => {});
      }
      return;
    }

    // Request permission
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      Alert.alert(
        'Permission Required',
        'Enable notifications in your device settings to receive RiskRadar alerts.',
        [{ text: 'OK' }]
      );
      return;
    }

    // Get push token and save to backend
    const tokenData = await Notifications.getExpoPushTokenAsync();
    const token = tokenData.data;
    setPushEnabled(true);

    if (isLoggedIn && user) {
      apiFetch(`/users/${user.id}/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_token: token }),
      }).catch(() => {});
    }
  };

  const handleLogout = async () => {
    if (user && !isDevUserMode) {
      await logout();
    }
    router.replace('/');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={palette.background} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Ionicons name="arrow-back" size={24} color={palette.text} />
        </TouchableOpacity>
        <Image source={brandLogo} style={styles.headerLogo} resizeMode="contain" />
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        
        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          <Text style={styles.sectionSubtitle}>Manage how RiskRadar alerts you</Text>
          
          <View style={styles.card}>
            <View style={styles.row}>
              <View style={styles.rowTextContainer}>
                <Text style={styles.rowTitle}>Push Notifications</Text>
                <Text style={styles.rowSubtitle}>Receive alerts on your device</Text>
              </View>
              <Switch
                value={pushEnabled}
                onValueChange={handlePushToggle}
                trackColor={{ false: palette.border, true: palette.primary }}
                thumbColor={palette.white}
              />
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <View style={styles.rowTextContainer}>
                <Text style={styles.rowTitle}>Email Alerts</Text>
                <Text style={styles.rowSubtitle}>Daily summaries and severe weather</Text>
              </View>
              <Switch
                value={emailEnabled}
                onValueChange={setEmailEnabled}
                trackColor={{ false: palette.border, true: palette.primary }}
                thumbColor={palette.white}
              />
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <View style={styles.rowTextContainer}>
                <Text style={styles.rowTitle}>SMS Alerts</Text>
                <Text style={styles.rowSubtitle}>Text messages for critical warnings</Text>
              </View>
              <Switch
                value={smsEnabled}
                onValueChange={setSmsEnabled}
                trackColor={{ false: palette.border, true: palette.primary }}
                thumbColor={palette.white}
              />
            </View>
          </View>
        </View>

        {/* Location Section - Only visible to authenticated users */}
        {isLoggedIn && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Location Preferences</Text>
            <Text style={styles.sectionSubtitle}>Set your default risk radar areas</Text>
            
            <View style={styles.card}>
              <View style={styles.row}>
                <View style={styles.rowTextContainer}>
                  <Text style={styles.rowTitle}>Use Device Location</Text>
                  <Text style={styles.rowSubtitle}>Automatically update risk based on GPS</Text>
                </View>
                <Switch
                  value={useGps}
                  onValueChange={setUseGps}
                  trackColor={{ false: palette.border, true: palette.primary }}
                  thumbColor={palette.white}
                />
              </View>
              
              {!useGps && (
                <>
                  <View style={styles.divider} />
                  <View style={{ paddingVertical: Spacing.sm + 4 }}>
                    <Text style={styles.label}>Home Zip Code</Text>
                    <View style={styles.inputContainer}>
                      <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                      <TextInput
                        style={styles.input}
                        placeholder="Enter 5-digit zip code"
                        placeholderTextColor={palette.textSecondary}
                        keyboardType="number-pad"
                        maxLength={5}
                        value={zipCode}
                        onChangeText={setZipCode}
                      />
                    </View>
                  </View>
                </>
              )}
            </View>
          </View>
        )}

        {/* Developer / Mock Mode Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Developer Tools</Text>
          <Text style={styles.sectionSubtitle}>Test different app states</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <View style={styles.rowTextContainer}>
                <Text style={styles.rowTitle}>Simulate User Mode</Text>
                <Text style={styles.rowSubtitle}>Forces an authenticated state</Text>
              </View>
              <Switch
                value={isDevUserMode}
                onValueChange={toggleDevUserMode}
                trackColor={{ false: palette.border, true: palette.primary }}
                thumbColor={palette.white}
              />
            </View>
          </View>
        </View>

        {/* Logout */}
        <View style={styles.footerSection}>
          <PrimaryButton
            label={isLoggedIn ? "Log Out (Return to Home)" : "Return to Home"}
            onPress={handleLogout}
            style={isLoggedIn ? { backgroundColor: palette.danger } : undefined}
          />
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

function getStyles(palette: typeof Colors.light) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: palette.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: Spacing.lg,
      paddingTop: SafeArea.paddingTop,
      paddingBottom: Spacing.md,
      backgroundColor: palette.card,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    backButton: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: palette.surfaceMuted,
      justifyContent: 'center',
      alignItems: 'center',
    },
    headerLogo: {
      width: 32,
      height: 32,
      marginRight: Spacing.sm,
    },
    headerTitle: {
      ...Typography.sectionLabel,
      color: palette.text,
    },
    headerSpacer: {
      width: 44,
    },
    scrollContent: {
      padding: Spacing.lg,
      paddingBottom: 60,
    },
    section: {
      marginBottom: Spacing.xl,
    },
    sectionTitle: {
      ...Typography.subtitle,
      color: palette.text,
      marginBottom: Spacing.xs,
    },
    sectionSubtitle: {
      ...Typography.meta,
      fontSize: 14,
      color: palette.textSecondary,
      marginBottom: Spacing.md,
    },
    card: {
      backgroundColor: palette.card,
      borderRadius: Radius.md,
      paddingHorizontal: Spacing.md,
      borderWidth: 1,
      borderColor: palette.border,
      ...Shadows.card,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: Spacing.md,
    },
    rowTextContainer: {
      flex: 1,
      paddingRight: Spacing.md,
    },
    rowTitle: {
      ...Typography.cardHeading,
      color: palette.text,
      marginBottom: Spacing.xs,
    },
    rowSubtitle: {
      ...Typography.meta,
      fontSize: 13,
      color: palette.textSecondary,
    },
    divider: {
      height: 1,
      backgroundColor: palette.border,
    },
    label: {
      ...Typography.meta,
      fontSize: 14,
      fontWeight: '500',
      color: palette.text,
      marginBottom: Spacing.sm,
    },
    inputContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.surfaceMuted,
      borderWidth: 1,
      borderColor: palette.border,
      borderRadius: Radius.sm,
      paddingHorizontal: Spacing.md,
      height: 50,
    },
    inputIcon: {
      marginRight: Spacing.sm,
    },
    input: {
      flex: 1,
      ...Typography.cardHeading,
      fontWeight: '400',
      color: palette.text,
      height: '100%',
    },
    footerSection: {
      marginTop: Spacing.md,
    },
  });
}
