import React, { useState } from 'react';
import {
  View,
  Text,
  Switch,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Platform,
  StatusBar,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { PrimaryButton } from '@/components/ui/PrimaryButton';

export default function SettingsScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  
  const { user, isLoggedIn, logout, isDevUserMode, toggleDevUserMode } = useAuth();

  // Local state for toggles (mocked for now, not saved to DB)
  const [pushEnabled, setPushEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [useGps, setUseGps] = useState(false);
  const [zipCode, setZipCode] = useState(user?.zip_code || '');

  const handleLogout = async () => {
    if (user && !isDevUserMode) {
      await logout();
    }
    router.replace('/');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle={scheme === 'dark' ? 'light-content' : 'dark-content'} backgroundColor={palette.background} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color={palette.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 40 }} /> {/* Spacer for alignment */}
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
                onValueChange={setPushEnabled}
                trackColor={{ false: palette.border, true: palette.primary }}
                thumbColor={Platform.OS === 'ios' ? '#FFFFFF' : pushEnabled ? palette.primary : '#f4f3f4'}
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
                thumbColor={Platform.OS === 'ios' ? '#FFFFFF' : emailEnabled ? palette.primary : '#f4f3f4'}
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
                thumbColor={Platform.OS === 'ios' ? '#FFFFFF' : smsEnabled ? palette.primary : '#f4f3f4'}
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
                  thumbColor={Platform.OS === 'ios' ? '#FFFFFF' : useGps ? palette.primary : '#f4f3f4'}
                />
              </View>
              
              {!useGps && (
                <>
                  <View style={styles.divider} />
                  <View style={{ paddingVertical: 12 }}>
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
                thumbColor={Platform.OS === 'ios' ? '#FFFFFF' : isDevUserMode ? palette.primary : '#f4f3f4'}
              />
            </View>
          </View>
        </View>

        {/* Logout */}
        <View style={styles.footerSection}>
          <PrimaryButton
            label={isLoggedIn ? "Log Out (Return to Home)" : "Return to Home"}
            onPress={handleLogout}
            style={isLoggedIn ? ({ backgroundColor: palette.danger, shadowColor: palette.danger } as any) : undefined}
          />
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

function getStyles(palette: typeof Colors.light | typeof Colors.dark) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: palette.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 24,
      paddingTop: Platform.OS === 'android' ? 16 : 0,
      paddingBottom: 16,
      backgroundColor: palette.card,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    backButton: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: palette.surfaceMuted,
      justifyContent: 'center',
      alignItems: 'center',
    },
    headerTitle: {
      fontSize: 20,
      fontWeight: '700',
      color: palette.text,
    },
    scrollContent: {
      padding: 24,
      paddingBottom: 60,
    },
    section: {
      marginBottom: 32,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '700',
      color: palette.text,
      marginBottom: 4,
    },
    sectionSubtitle: {
      fontSize: 14,
      color: palette.textSecondary,
      marginBottom: 16,
    },
    card: {
      backgroundColor: palette.card,
      borderRadius: 16,
      paddingHorizontal: 16,
      borderWidth: 1,
      borderColor: palette.border,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.03,
      shadowRadius: 8,
      elevation: 2,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: 16,
    },
    rowTextContainer: {
      flex: 1,
      paddingRight: 16,
    },
    rowTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: palette.text,
      marginBottom: 4,
    },
    rowSubtitle: {
      fontSize: 13,
      color: palette.textSecondary,
    },
    divider: {
      height: 1,
      backgroundColor: palette.border,
    },
    label: {
      fontSize: 14,
      fontWeight: '500',
      color: palette.text,
      marginBottom: 8,
    },
    inputContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.surfaceMuted,
      borderWidth: 1,
      borderColor: palette.border,
      borderRadius: 12,
      paddingHorizontal: 16,
      height: 50,
    },
    inputIcon: {
      marginRight: 10,
    },
    input: {
      flex: 1,
      fontSize: 16,
      color: palette.text,
      height: '100%',
    },
    footerSection: {
      marginTop: 16,
    },
  });
}
