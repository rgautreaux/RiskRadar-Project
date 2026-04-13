import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors, Spacing, Radius, Shadows, Typography, SafeArea } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

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
  zip_code: string | null;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
}

interface ForecastPeriod {
  date: string;
  day_name: string;
  high_temp: number;
  low_temp: number;
  description: string;
  weather_main: string;
  icon_code: string;
  wind_mph: number;
  precip_chance: number;
  humidity: number;
  uvi: number;
}

function forecastIcon(weatherMain: string): keyof typeof Ionicons.glyphMap {
  const w = weatherMain.toLowerCase();
  if (w === 'thunderstorm') return 'thunderstorm-outline';
  if (w === 'snow') return 'snow-outline';
  if (w === 'rain' || w === 'drizzle') return 'rainy-outline';
  if (w === 'atmosphere') return 'water-outline';
  if (w === 'clouds') return 'cloudy-outline';
  return 'sunny-outline';
}

function forecastIconColor(weatherMain: string, palette: typeof Colors.light): string {
  const w = weatherMain.toLowerCase();
  if (w === 'thunderstorm' || w === 'clouds') return palette.textSecondary;
  if (w === 'snow' || w === 'rain' || w === 'drizzle') return palette.primary;
  if (w === 'atmosphere') return palette.textSecondary;
  return palette.warning;
}

export default function WeatherReport() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { isLoggedIn } = useAuth();
  const params = useLocalSearchParams();
  // Accept either "query" (new) or "zipCode" (legacy) param
  const rawQuery = params.query ?? params.zipCode;
  const query = (Array.isArray(rawQuery) ? rawQuery[0] : rawQuery ?? '').trim();

  const [summary, setSummary] = useState<Summary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [locationInfo, setLocationInfo] = useState<LocationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [forecast, setForecast] = useState<ForecastPeriod[]>([]);

  const fetchData = async () => {
    setError(null);
    setLoading(true);
    try {
      if (!query || query.length < 2) {
        setError('Please provide a valid city name or zip code.');
        return;
      }

      // Step 1: Resolve the query (city name or zip) to coordinates via /location/search
      const loc = await apiFetch<LocationInfo>(
        `/location/search?q=${encodeURIComponent(query)}`
      );
      setLocationInfo(loc);

      // Step 2: Fetch alerts — use zip if available, otherwise use lat/lon/state
      const alertsParam = loc.zip_code
        ? `zip_code=${loc.zip_code}`
        : `lat=${loc.latitude}&lon=${loc.longitude}&state=${loc.state}`;
      const alertsPromise = apiFetch<AlertItem[]>(`/location/alerts?${alertsParam}`).catch(() => []);

      // Step 3: Summaries — only zip-based endpoints are available, so use zip if we have one
      const summaryPromises: [Promise<Summary | null>, Promise<Summary | null>] = loc.zip_code
        ? [
            apiFetch<Summary | null>(`/summaries/generate/local?zip_code=${loc.zip_code}`, { method: 'POST' }).catch(() => null),
            apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${loc.zip_code}`).catch(() => null),
          ]
        : [Promise.resolve(null), Promise.resolve(null)];

      const [alertsData, generatedSummary, latestSummary] = await Promise.all([
        alertsPromise,
        ...summaryPromises,
      ]);

      const summaryToUse = generatedSummary ?? latestSummary ?? null;

      setSummary(summaryToUse);
      setAlerts(alertsData ?? []);

      // Step 4: Fetch 7-day OpenWeatherMap forecast (fire-and-forget)
      apiFetch<ForecastPeriod[]>(`/forecast?lat=${loc.latitude}&lon=${loc.longitude}`)
        .then(periods => setForecast(periods))
        .catch(() => {});

      // Check if this location is already saved
      if (isLoggedIn && loc) {
        apiFetch<{ id: number; city: string; state: string }[]>('/users/destinations')
          .then(destinations => {
            const already = destinations.some(
              d => d.city.toLowerCase() === loc.city.toLowerCase() && d.state === loc.state
            );
            setIsSaved(already);
          })
          .catch(() => {});
      }
    } catch {
      setError('Failed to load weather report. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (!isLoggedIn) {
      router.push('/auth/login');
      return;
    }
    if (!locationInfo || isSaved || isSaving) return;
    setIsSaving(true);
    try {
      await apiFetch('/users/destinations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          city: locationInfo.city,
          state: locationInfo.state,
          zip_code: locationInfo.zip_code,
          latitude: locationInfo.latitude,
          longitude: locationInfo.longitude,
        }),
      });
      setIsSaved(true);
    } catch {
      // 409 = already saved
      setIsSaved(true);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [query]);

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
        <Text style={styles.headerTitle}>Weather Report</Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={handleBookmark}
          disabled={isSaving}
          accessibilityRole="button"
          accessibilityLabel={isSaved ? 'Location saved' : 'Save location'}
          accessibilityState={{ disabled: isSaving }}
        >
          <Ionicons
            name={isSaved ? 'bookmark' : 'bookmark-outline'}
            size={24}
            color={isSaved ? palette.primary : palette.text}
          />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <StateView
          state={loading ? 'loading' : error ? 'error' : 'success'}
          loadingText="Loading weather report..."
          errorText={error || 'Failed to load report'}
          onRetry={fetchData}
        >
          {/* Location Header */}
          <View style={styles.mainWeatherCard}>
            <Text style={styles.locationText}>
              {locationInfo
                ? `${locationInfo.city}, ${locationInfo.state}${locationInfo.zip_code ? ` ${locationInfo.zip_code}` : ''}`
                : query}
            </Text>
            <View style={styles.tempContainer}>
              <Ionicons name="partly-sunny" size={80} color={palette.warning} />
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

          {/* 7-Day Forecast */}
          {forecast.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>7-Day Forecast</Text>
              <View style={styles.summaryCard}>
                {forecast.map((period, i) => {
                  const dayLabel = period.day_name.slice(0, 3);
                  const icon = forecastIcon(period.weather_main);
                  const iconColor = forecastIconColor(period.weather_main, palette);
                  return (
                    <React.Fragment key={i}>
                      {i > 0 && <View style={styles.forecastDivider} />}
                      <View style={styles.forecastRow}>
                        <Text style={styles.forecastDay}>{dayLabel}</Text>
                        <Ionicons name={icon} size={22} color={iconColor} />
                        <Text style={styles.forecastDesc} numberOfLines={1}>{period.description}</Text>
                        <View style={styles.forecastRight}>
                          {period.precip_chance > 0 && (
                            <Text style={styles.forecastPrecip}>
                              <Ionicons name="water-outline" size={11} color={palette.primary} />{' '}
                              {period.precip_chance}%
                            </Text>
                          )}
                          <Text style={styles.forecastTemp}>
                            {Math.round(period.high_temp)}° / {Math.round(period.low_temp)}°
                          </Text>
                        </View>
                      </View>
                    </React.Fragment>
                  );
                })}
              </View>
            </View>
          )}

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
      paddingHorizontal: Spacing.md,
      paddingTop: SafeArea.paddingTop,
      paddingBottom: Spacing.md,
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
    headerLogo: {
      width: 32,
      height: 32,
    },
    headerTitle: {
      ...Typography.subtitle,
      flex: 1,
      color: palette.text,
    },
    scrollContent: {
      padding: Spacing.lg,
      paddingBottom: Spacing.xxl,
    },
    mainWeatherCard: {
      alignItems: 'center',
      marginBottom: Spacing.xl,
    },
    locationText: {
      ...Typography.sectionLabel,
      color: palette.text,
      marginBottom: Spacing.md,
    },
    tempContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
    },
    section: {
      marginBottom: Spacing.lg,
    },
    sectionTitle: {
      ...Typography.sectionLabel,
      color: palette.text,
      marginBottom: Spacing.sm,
    },
    summaryCard: {
      backgroundColor: palette.card,
      borderRadius: Radius.lg,
      padding: Spacing.md + 4,
      ...Shadows.card,
      borderWidth: 1,
      borderColor: palette.border,
    },
    summaryHeading: {
      ...Typography.cardHeading,
      fontWeight: '700',
      color: palette.text,
      marginBottom: Spacing.sm,
    },
    summaryText: {
      ...Typography.body,
      fontSize: 16,
      lineHeight: 24,
      color: palette.textSecondary,
    },
    summaryMeta: {
      ...Typography.meta,
      color: palette.textSecondary,
      marginTop: Spacing.sm,
    },
    alertRow: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.card,
      borderRadius: Radius.md,
      padding: Spacing.md,
      marginBottom: Spacing.sm,
      borderWidth: 1,
      borderColor: palette.border,
    },
    severityDot: {
      width: 12,
      height: 12,
      borderRadius: 6,
      marginRight: Spacing.sm,
    },
    alertRowText: {
      flex: 1,
    },
    alertTitle: {
      ...Typography.body,
      fontWeight: '600',
      color: palette.text,
    },
    alertMeta: {
      ...Typography.meta,
      fontSize: 13,
      color: palette.textSecondary,
      marginTop: 2,
      textTransform: 'capitalize',
    },
    forecastRow: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: Spacing.sm + 4,
      gap: Spacing.sm,
    },
    forecastDivider: {
      height: 1,
      backgroundColor: palette.border,
    },
    forecastDay: {
      ...Typography.meta,
      fontSize: 14,
      fontWeight: '600',
      color: palette.text,
      width: 72,
    },
    forecastDesc: {
      flex: 1,
      ...Typography.meta,
      fontSize: 13,
      color: palette.textSecondary,
    },
    forecastRight: {
      alignItems: 'flex-end',
    },
    forecastTemp: {
      ...Typography.body,
      fontWeight: '700',
      color: palette.text,
    },
    forecastPrecip: {
      ...Typography.meta,
      fontSize: 11,
      color: palette.primary,
      marginBottom: 2,
    },
  });
}
