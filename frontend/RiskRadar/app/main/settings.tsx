import React, { useEffect, useState } from 'react';
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
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { PrimaryButton } from '@/components/ui/PrimaryButton';
import { apiFetch } from '@/utils/api';

const DEMO_SETTINGS_KEY = 'riskradar_demo_settings';

interface ScrapeResultItem {
  source: string;
  status: string;
  alerts_stored?: number;
  error?: string;
}

export default function SettingsScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  
  const { user, isLoggedIn, logout, isDevUserMode, toggleDevUserMode, savePreferences } = useAuth();

  // Local state for toggles (mocked for now, not saved to DB)
  const [pushEnabled, setPushEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [useGps, setUseGps] = useState(false);
  const [zipCode, setZipCode] = useState(user?.zip_code || '');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [healthStatus, setHealthStatus] = useState<'idle' | 'checking' | 'healthy' | 'unhealthy'>('idle');
  const [healthDetail, setHealthDetail] = useState('');
  const [scrapeStatus, setScrapeStatus] = useState<'idle' | 'triggering' | 'done' | 'error'>('idle');
  const [scrapeDetail, setScrapeDetail] = useState('');
  const [scrapeResults, setScrapeResults] = useState<ScrapeResultItem[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const stored = await AsyncStorage.getItem(DEMO_SETTINGS_KEY);
        if (stored) {
          const parsed = JSON.parse(stored) as {
            pushEnabled?: boolean;
            emailEnabled?: boolean;
            smsEnabled?: boolean;
            useGps?: boolean;
            zipCode?: string;
          };
          if (typeof parsed.pushEnabled === 'boolean') setPushEnabled(parsed.pushEnabled);
          if (typeof parsed.emailEnabled === 'boolean') setEmailEnabled(parsed.emailEnabled);
          if (typeof parsed.smsEnabled === 'boolean') setSmsEnabled(parsed.smsEnabled);
          if (typeof parsed.useGps === 'boolean') setUseGps(parsed.useGps);
          if (typeof parsed.zipCode === 'string') setZipCode(parsed.zipCode);
        } else if (user?.zip_code) {
          setZipCode(user.zip_code);
        }
      } catch {
        // Keep the screen usable even if local demo settings cannot be loaded.
      }
    })();
  }, [user?.zip_code]);

  useEffect(() => {
    if (user?.zip_code && !zipCode) {
      setZipCode(user.zip_code);
    }
  }, [user?.zip_code, zipCode]);

  const handleSaveDemoSettings = async () => {
    setSaveStatus('saving');
    try {
      const nextSettings = {
        pushEnabled,
        emailEnabled,
        smsEnabled,
        useGps,
        zipCode: zipCode.trim(),
      };

      await AsyncStorage.setItem(DEMO_SETTINGS_KEY, JSON.stringify(nextSettings));

      const shouldSaveRemoteZip = isLoggedIn && !isDevUserMode && nextSettings.zipCode.length === 5;
      if (shouldSaveRemoteZip) {
        await savePreferences({ zip_code: nextSettings.zipCode });
      }

      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    }
  };

  const handleCheckHealth = async () => {
    setHealthStatus('checking');
    setHealthDetail('');
    try {
      const response = await apiFetch<{ status: string; alert_count?: number; database?: string }>('/health');
      setHealthStatus(response.status === 'healthy' ? 'healthy' : 'unhealthy');
      setHealthDetail(
        response.status === 'healthy'
          ? `Backend healthy${typeof response.alert_count === 'number' ? `, ${response.alert_count} alerts indexed` : ''}.`
          : 'Backend reported an unhealthy state.'
      );
    } catch (error) {
      setHealthStatus('unhealthy');
      setHealthDetail(error instanceof Error ? error.message : 'Unable to reach the backend health endpoint.');
    }
  };

  const handleTriggerScrape = async () => {
    setScrapeStatus('triggering');
    setScrapeDetail('');
    setScrapeResults([]);
    try {
      const response = await apiFetch<{ triggered_at: string; results: ScrapeResultItem[] }>('/scrape/trigger', {
        method: 'POST',
      });
      const successCount = response.results.filter((item) => item.status === 'success').length;
      const errorCount = response.results.filter((item) => item.status === 'error').length;
      setScrapeStatus('done');
      setScrapeDetail(`Triggered ${response.results.length} scrapers: ${successCount} success, ${errorCount} error.`);
      setScrapeResults(response.results);
    } catch (error) {
      setScrapeStatus('error');
      setScrapeDetail(error instanceof Error ? error.message : 'Could not trigger the scrape pipeline.');
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/welcome');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={palette.background} />
      
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

        {/* Backend Demo Tools */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Backend Demo Tools</Text>
          <Text style={styles.sectionSubtitle}>Show system health and data refresh capability</Text>
          <View style={styles.card}>
            <View style={styles.backendActionRow}>
              <PrimaryButton
                label={healthStatus === 'checking' ? 'Checking...' : 'Check Backend Health'}
                onPress={handleCheckHealth}
                loading={healthStatus === 'checking'}
                style={styles.backendButton}
              />
              <PrimaryButton
                label={scrapeStatus === 'triggering' ? 'Triggering...' : 'Trigger Scrape'}
                onPress={handleTriggerScrape}
                loading={scrapeStatus === 'triggering'}
                style={styles.backendButton}
                disabled={!isLoggedIn || isDevUserMode}
              />
            </View>
            <Text style={styles.backendNote}>
              Backend health is public. Scrape trigger requires a real authenticated session.
            </Text>
            {healthDetail ? (
              <Text style={[styles.backendResult, healthStatus === 'healthy' ? styles.backendSuccess : styles.backendError]}>
                {healthDetail}
              </Text>
            ) : null}
            {scrapeDetail ? (
              <Text style={[styles.backendResult, scrapeStatus === 'done' ? styles.backendSuccess : styles.backendError]}>
                {scrapeDetail}
              </Text>
            ) : null}
            {scrapeResults.length > 0 ? (
              <View style={styles.scrapeResultsList}>
                {scrapeResults.map((item) => (
                  <View key={item.source} style={styles.scrapeResultRow}>
                    <Text style={styles.scrapeSource}>{item.source}</Text>
                    <Text style={[styles.scrapeOutcome, item.status === 'success' ? styles.backendSuccess : styles.backendError]}>
                      {item.status === 'success'
                        ? `stored ${item.alerts_stored ?? 0}`
                        : item.error || 'error'}
                    </Text>
                  </View>
                ))}
              </View>
            ) : null}
          </View>
        </View>

        {/* Logout */}
        <View style={styles.footerSection}>
          <PrimaryButton
            label={saveStatus === 'saving' ? 'Saving...' : 'Save Demo Settings'}
            onPress={handleSaveDemoSettings}
            style={{ marginBottom: 12 }}
            disabled={saveStatus === 'saving'}
            loading={saveStatus === 'saving'}
          />
          {saveStatus === 'saved' ? (
            <Text style={[styles.sectionSubtitle, { textAlign: 'center', marginBottom: 12 }]}>
              Demo settings saved.
            </Text>
          ) : null}
          {saveStatus === 'error' ? (
            <Text style={[styles.sectionSubtitle, { textAlign: 'center', marginBottom: 12, color: palette.danger }]}>
              Could not save settings. Local demo preferences were still updated.
            </Text>
          ) : null}
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
    backendActionRow: {
      marginTop: 8,
    },
    backendButton: {
      marginBottom: 12,
    },
    backendNote: {
      fontSize: 12,
      color: palette.textSecondary,
      marginTop: 4,
    },
    backendResult: {
      fontSize: 13,
      marginTop: 10,
      lineHeight: 18,
    },
    scrapeResultsList: {
      marginTop: 10,
      borderTopWidth: 1,
      borderTopColor: palette.border,
      paddingTop: 10,
      gap: 8,
    },
    scrapeResultRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 8,
    },
    scrapeSource: {
      fontSize: 12,
      color: palette.text,
      fontWeight: '600',
      textTransform: 'uppercase',
    },
    scrapeOutcome: {
      flex: 1,
      textAlign: 'right',
      fontSize: 12,
    },
    backendSuccess: {
      color: palette.success,
    },
    backendError: {
      color: palette.danger,
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
