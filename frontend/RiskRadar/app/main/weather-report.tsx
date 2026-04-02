import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Platform,
  StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

interface Summary {
  id: number;
  title: string;
  content: string;
  summary_type: string;
  region: string | null;
  generated_at: string;
  model_used: string | null;
}

interface AlertItem {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  description: string | null;
  location_name: string | null;
}

interface LocationInfo {
  zip_code: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
}

export default function WeatherReport() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const params = useLocalSearchParams();
  const rawZipCode = params.zipCode;
  const zipCode = Array.isArray(rawZipCode) ? rawZipCode[0] : rawZipCode ?? 'Unknown Location';

  const [summary, setSummary] = useState<Summary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [locationInfo, setLocationInfo] = useState<LocationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setError(null);
        const isValidZip = zipCode.length === 5 && /^\d{5}$/.test(zipCode);

        // Fetch location info, on-demand alerts, and latest summary in parallel
        const promises: Promise<any>[] = [
          apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${zipCode}`).catch(() => null)
        ];

        if (isValidZip) {
          promises.push(
            apiFetch<LocationInfo>(`/location/info?zip_code=${zipCode}`).catch(() => null),
            apiFetch<AlertItem[]>(`/location/alerts?zip_code=${zipCode}`).catch(() => []),
            apiFetch<Summary | null>(`/summaries/generate/local?zip_code=${zipCode}`, { method: 'POST' }).catch(() => null),
            apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${zipCode}`).catch(() => null)
          );
        } else {
          promises.push(Promise.resolve(null), Promise.resolve([]));
        }

        const [summaryData, locInfo, alertsData] = await Promise.all(promises);
        setSummary(summaryData);
        setLocationInfo(locInfo);
        setAlerts(alertsData ?? []);
      } catch {
        setError('Failed to load weather report. Please check your connection.');
      } finally {
        setLoading(false);
      }
    })();
  }, [zipCode]);

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
        <Text style={styles.headerTitle}>Weather Report</Text>
        <View style={{ width: 44 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <StateView
          state={loading ? 'loading' : error ? 'error' : 'success'}
          loadingText="Loading weather report..."
          errorText={error || 'Failed to load report'}
          onRetry={() => {
            setLoading(true);
            setError(null);
            // Retry the fetch
            (async () => {
              try {
                const isValidZip = zipCode.length === 5 && /^\d{5}$/.test(zipCode);
                const promises: Promise<any>[] = [
                  apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${zipCode}`).catch(() => null)
                ];
                if (isValidZip) {
                  promises.push(
                    apiFetch<LocationInfo>(`/location/info?zip_code=${zipCode}`).catch(() => null),
                    apiFetch<AlertItem[]>(`/location/alerts?zip_code=${zipCode}`).catch(() => []),
                    apiFetch<Summary | null>(`/summaries/generate/local?zip_code=${zipCode}`, { method: 'POST' }).catch(() => null),
                    apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${zipCode}`).catch(() => null)
                  );
                } else {
                  promises.push(Promise.resolve(null), Promise.resolve([]));
                }
                const [summaryData, locInfo, alertsData] = await Promise.all(promises);
                setSummary(summaryData);
                setLocationInfo(locInfo);
                setAlerts(alertsData ?? []);
              } catch {
                setError('Failed to load weather report. Please check your connection.');
              } finally {
                setLoading(false);
              }
            })();
          }}
        >
          {/* Location Header */}
          <View style={styles.mainWeatherCard}>
            <Text style={styles.locationText}>
              {locationInfo
                ? `${locationInfo.city}, ${locationInfo.state} ${zipCode}`
                : `Location: ${zipCode}`}
            </Text>
            <View style={styles.tempContainer}>
              <Ionicons name="partly-sunny" size={80} color="#F59E0B" />
            </View>
          </View>

          {/* AI Summary */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>AI Summary</Text>
            <View style={styles.summaryCard}>
              {summary ? (
                <>
                  <Text style={styles.summaryHeading}>{summary.title}</Text>
                  <Text style={styles.summaryText}>{summary.content}</Text>
                  <Text style={styles.summaryMeta}>
                    Generated {new Date(summary.generated_at).toLocaleString()}
                    {summary.model_used ? ` via ${summary.model_used}` : ''}
                  </Text>
                </>
              ) : (
                <Text style={styles.summaryText}>
                  No summary available yet. The backend generates summaries from active alerts.
                </Text>
              )}
            </View>
          </View>

          {/* Active Alerts Summary */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Alerts</Text>
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <View key={alert.id} style={styles.alertRow}>
                  <View style={[styles.severityDot, {
                    backgroundColor: alert.severity.toLowerCase().includes('critical') || alert.severity.toLowerCase().includes('extreme')
                      ? palette.danger
                      : alert.severity.toLowerCase().includes('warning') || alert.severity.toLowerCase().includes('severe')
                        ? palette.warning
                        : palette.primary,
                  }]} />
                  <View style={styles.alertRowText}>
                    <Text style={styles.alertTitle}>{alert.title}</Text>
                    <Text style={styles.alertMeta}>{alert.alert_type} - {alert.severity}</Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.summaryCard}>
                <Text style={styles.summaryText}>No active alerts for this area.</Text>
              </View>
            )}
          </View>
        </StateView>
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
      paddingHorizontal: 16,
      paddingTop: Platform.OS === 'android' ? 16 : 0,
      paddingBottom: 16,
      backgroundColor: palette.card,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    backButton: {
      width: 44,
      height: 44,
      justifyContent: 'center',
      alignItems: 'center',
    },
    headerTitle: {
      fontSize: 18,
      fontWeight: '700',
      color: palette.text,
    },
    scrollContent: {
      padding: 24,
      paddingBottom: 40,
    },
    mainWeatherCard: {
      alignItems: 'center',
      marginBottom: 32,
    },
    locationText: {
      fontSize: 20,
      fontWeight: '600',
      color: palette.text,
      marginBottom: 16,
    },
    tempContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
    },
    section: {
      marginBottom: 24,
    },
    sectionTitle: {
      fontSize: 20,
      fontWeight: '700',
      color: palette.text,
      marginBottom: 12,
    },
    summaryCard: {
      backgroundColor: palette.card,
      borderRadius: 20,
      padding: 20,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.05,
      shadowRadius: 12,
      elevation: 4,
      borderWidth: 1,
      borderColor: palette.border,
    },
    summaryHeading: {
      fontSize: 16,
      fontWeight: '700',
      color: palette.text,
      marginBottom: 8,
    },
    summaryText: {
      fontSize: 16,
      lineHeight: 24,
      color: palette.textSecondary,
    },
    summaryMeta: {
      fontSize: 12,
      color: palette.textSecondary,
      marginTop: 12,
    },
    alertRow: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.card,
      borderRadius: 16,
      padding: 16,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: palette.border,
    },
    severityDot: {
      width: 12,
      height: 12,
      borderRadius: 6,
      marginRight: 12,
    },
    alertRowText: {
      flex: 1,
    },
    alertTitle: {
      fontSize: 15,
      fontWeight: '600',
      color: palette.text,
    },
    alertMeta: {
      fontSize: 13,
      color: palette.textSecondary,
      marginTop: 2,
      textTransform: 'capitalize',
    },
  });
}
