import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Platform,
  StatusBar,
  Animated,
  ViewStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

function FadeInView({ delay = 0, children, style }: { delay?: number; children: React.ReactNode; style?: ViewStyle }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(18)).current;
  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 450, useNativeDriver: true }),
        Animated.timing(translateY, { toValue: 0, duration: 450, useNativeDriver: true }),
      ]).start();
    }, delay);
    return () => clearTimeout(timer);
  }, []);
  return <Animated.View style={[style, { opacity, transform: [{ translateY }] }]}>{children}</Animated.View>;
}

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

interface ForecastDay {
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

interface LocationInfo {
  zip_code: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
}

/** Map OWM weather_main to an Ionicon name */
function weatherIcon(main: string): keyof typeof Ionicons.glyphMap {
  const m = main.toLowerCase();
  if (m.includes('thunder')) return 'thunderstorm-outline';
  if (m.includes('drizzle') || m.includes('rain')) return 'rainy-outline';
  if (m.includes('snow')) return 'snow-outline';
  if (m.includes('cloud')) return 'cloudy-outline';
  if (m.includes('clear')) return 'sunny-outline';
  if (['mist', 'smoke', 'haze', 'fog'].some(w => m.includes(w))) return 'water-outline';
  return 'partly-sunny-outline';
}

export default function WeatherReport() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const params = useLocalSearchParams();
  const rawZipCode = params.zipCode;
  const rawQuery = params.q;
  const zipCode = Array.isArray(rawZipCode) ? rawZipCode[0] : rawZipCode;
  const searchQuery = Array.isArray(rawQuery) ? rawQuery[0] : rawQuery;

  const [summary, setSummary] = useState<Summary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [locationInfo, setLocationInfo] = useState<LocationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWeatherReport = async () => {
    let resolvedZip: string | null = null;
    let locInfo: LocationInfo | null = null;

    if (zipCode && /^\d{5}$/.test(zipCode)) {
      resolvedZip = zipCode;
      locInfo = await apiFetch<LocationInfo>(`/location/info?zip_code=${zipCode}`).catch(() => null);
    } else if (searchQuery && searchQuery.trim().length >= 2) {
      try {
        const searchResult = await apiFetch<LocationInfo>(
          `/location/search?q=${encodeURIComponent(searchQuery.trim())}`
        );
        locInfo = searchResult;
        resolvedZip = searchResult.zip_code;
      } catch {
        setError(`Could not find location for "${searchQuery}". Try a different city or zip code.`);
        return;
      }
    } else {
      setSummary(null);
      setLocationInfo(null);
      setAlerts([]);
      setForecast([]);
      setError('Please enter a valid city, state, or zip code.');
      return;
    }

    setLocationInfo(locInfo);

    const [alertsData, forecastData, summaryData] = await Promise.all([
      resolvedZip
        ? apiFetch<AlertItem[]>(`/location/alerts?zip_code=${resolvedZip}`).catch(() => [])
        : Promise.resolve([]),
      resolvedZip
        ? apiFetch<ForecastDay[]>(`/forecast/zip?zip_code=${resolvedZip}`).catch(() => [])
        : Promise.resolve([]),
      resolvedZip
        ? apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${resolvedZip}`).catch(() => null)
        : Promise.resolve(null),
    ]);

    setSummary(summaryData);
    setAlerts(alertsData ?? []);
    setForecast(forecastData ?? []);
  };

  useEffect(() => {
    (async () => {
      try {
        setError(null);
        await loadWeatherReport();
      } catch {
        setError('Failed to load weather report. Please check your connection.');
      } finally {
        setLoading(false);
      }
    })();
  }, [zipCode, searchQuery]);

  const displayLocation = locationInfo
    ? `${locationInfo.city}, ${locationInfo.state}${locationInfo.zip_code ? ` ${locationInfo.zip_code}` : ''}`
    : searchQuery || zipCode || 'Unknown';

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
            (async () => {
              try {
                await loadWeatherReport();
              } catch {
                setError('Failed to load weather report. Please check your connection.');
              } finally {
                setLoading(false);
              }
            })();
          }}
        >
          {/* Location Header */}
          <FadeInView delay={0} style={styles.mainWeatherCard}>
            <Text style={styles.locationText}>{displayLocation}</Text>
            {forecast.length > 0 ? (
              <>
                <Ionicons name={weatherIcon(forecast[0].weather_main)} size={80} color="#F59E0B" />
                <Text style={styles.currentTemp}>{Math.round(forecast[0].high_temp)}°F</Text>
                <Text style={styles.currentDesc}>{forecast[0].description}</Text>
                <Text style={styles.currentHiLo}>
                  H:{Math.round(forecast[0].high_temp)}°  L:{Math.round(forecast[0].low_temp)}°
                </Text>
              </>
            ) : (
              <View style={styles.tempContainer}>
                <Ionicons name="partly-sunny" size={80} color="#F59E0B" />
              </View>
            )}
          </FadeInView>

          {/* 7-Day Forecast */}
          {forecast.length > 1 && (
            <FadeInView delay={150} style={styles.section}>
              <Text style={styles.sectionTitle}>7-Day Forecast</Text>
              <View style={styles.summaryCard}>
                {forecast.map((day, i) => (
                  <View
                    key={day.date}
                    style={[
                      styles.forecastRow,
                      i < forecast.length - 1 && { borderBottomWidth: 1, borderBottomColor: palette.border },
                    ]}
                  >
                    <Text style={[styles.forecastDay, i === 0 && { fontWeight: '700', color: palette.primary }]}>
                      {i === 0 ? 'Today' : day.day_name.slice(0, 3)}
                    </Text>
                    <Ionicons name={weatherIcon(day.weather_main)} size={22} color="#F59E0B" />
                    {day.precip_chance > 0 && (
                      <Text style={styles.forecastPrecip}>{day.precip_chance}%</Text>
                    )}
                    <View style={styles.forecastTemps}>
                      <Text style={styles.forecastLow}>{Math.round(day.low_temp)}°</Text>
                      <View style={styles.tempBar}>
                        <View style={[styles.tempBarFill, { width: `${Math.min(100, ((day.high_temp - day.low_temp) / 30) * 100)}%` }]} />
                      </View>
                      <Text style={styles.forecastHigh}>{Math.round(day.high_temp)}°</Text>
                    </View>
                  </View>
                ))}
              </View>
            </FadeInView>
          )}

          {/* AI Summary */}
          <FadeInView delay={300} style={styles.section}>
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
          </FadeInView>

          {/* Active Alerts Summary */}
          <FadeInView delay={450} style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Alerts</Text>
            {alerts.length > 0 ? (
              alerts.map((alert, i) => (
                <FadeInView key={alert.id} delay={500 + i * 80}>
                  <View style={styles.alertRow}>
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
                </FadeInView>
              ))
            ) : (
              <View style={styles.summaryCard}>
                <Text style={styles.summaryText}>No active alerts for this area.</Text>
              </View>
            )}
          </FadeInView>
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
      fontSize: 28,
      fontWeight: '300',
      color: palette.text,
      marginBottom: 8,
    },
    currentTemp: {
      fontSize: 64,
      fontWeight: '200',
      color: palette.text,
      marginTop: 4,
    },
    currentDesc: {
      fontSize: 16,
      color: palette.textSecondary,
      textTransform: 'capitalize',
      marginTop: 2,
    },
    currentHiLo: {
      fontSize: 16,
      fontWeight: '500',
      color: palette.text,
      marginTop: 4,
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
    forecastRow: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: 12,
      gap: 10,
    },
    forecastDay: {
      width: 48,
      fontSize: 15,
      fontWeight: '500',
      color: palette.text,
    },
    forecastPrecip: {
      fontSize: 12,
      color: palette.primary,
      fontWeight: '600',
      width: 32,
    },
    forecastTemps: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'flex-end',
      gap: 8,
    },
    forecastHigh: {
      fontSize: 15,
      fontWeight: '600',
      color: palette.text,
      width: 32,
      textAlign: 'right',
    },
    forecastLow: {
      fontSize: 15,
      color: palette.textSecondary,
      width: 32,
      textAlign: 'right',
    },
    tempBar: {
      flex: 1,
      height: 4,
      backgroundColor: palette.border,
      borderRadius: 2,
      maxWidth: 80,
    },
    tempBarFill: {
      height: 4,
      backgroundColor: '#F59E0B',
      borderRadius: 2,
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
