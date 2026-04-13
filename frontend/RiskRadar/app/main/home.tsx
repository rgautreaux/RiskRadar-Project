import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Keyboard,
  Image,
  ActivityIndicator,
  Animated,
  Dimensions,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Colors, Spacing, Radius, Shadows, Typography, SafeArea } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');
const { width: SCREEN_WIDTH } = Dimensions.get('window');

// ── Interfaces ───────────────────────────────────────────────────────

interface AlertStats { total: number; by_type: Record<string, number>; by_severity: Record<string, number> }
interface Summary { id: number; title: string; content: string; summary_type: string; region: string | null; generated_at: string; model_used: string | null }
interface AutocompleteResult { label: string; city: string; state: string }
interface LocationInfo { zip_code: string | null; city: string; state: string; latitude: number; longitude: number }
interface AlertItem { id: number; alert_type: string; severity: string; title: string; description: string | null; location_name: string | null }
interface ForecastPeriod { date: string; day_name: string; high_temp: number; low_temp: number; description: string; weather_main: string; icon_code: string; wind_mph: number; precip_chance: number; humidity: number; uvi: number }

// ── Weather helpers ──────────────────────────────────────────────────

function weatherIcon(main: string): keyof typeof Ionicons.glyphMap {
  const w = main.toLowerCase();
  if (w === 'thunderstorm') return 'thunderstorm';
  if (w === 'snow') return 'snow';
  if (w === 'rain' || w === 'drizzle') return 'rainy';
  if (w === 'atmosphere') return 'water';
  if (w === 'clouds') return 'cloud';
  return 'sunny';
}

function weatherGradient(main: string): [string, string, string] {
  const w = main.toLowerCase();
  if (w === 'thunderstorm') return ['#1a1a2e', '#16213e', '#0f3460'];
  if (w === 'snow') return ['#4a6fa5', '#7b9cc2', '#aec6de'];
  if (w === 'rain' || w === 'drizzle') return ['#2c3e50', '#3d566e', '#4a6fa5'];
  if (w === 'clouds') return ['#536976', '#627d8c', '#748d9e'];
  return ['#2D6A4F', '#1B4332', '#0d2818']; // clear / default — matches brand
}

function weatherConditionText(main: string, desc: string): string {
  if (desc) return desc.charAt(0).toUpperCase() + desc.slice(1);
  return main;
}

const DEMO_SETTINGS_KEY = 'riskradar_demo_settings';

// ── Animated card wrapper ────────────────────────────────────────────

function FadeInView({ delay = 0, children, style }: { delay?: number; children: React.ReactNode; style?: any }) {
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

  return (
    <Animated.View style={[style, { opacity, transform: [{ translateY }] }]}>
      {children}
    </Animated.View>
  );
}

// ── Main component ───────────────────────────────────────────────────

export default function Home() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { user, isLoggedIn } = useAuth();
  const [searchQuery, setSearchQuery] = useState(user?.zip_code ?? '');
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [errorStats, setErrorStats] = useState<string | null>(null);
  const autocompleteTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [locationInfo, setLocationInfo] = useState<LocationInfo | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [forecast, setForecast] = useState<ForecastPeriod[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [errorSearch, setErrorSearch] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Animation key — bumps on each search to re-trigger fade-ins
  const [animKey, setAnimKey] = useState(0);

  useEffect(() => { if (user?.zip_code) setSearchQuery(user.zip_code); }, [user?.zip_code]);
  useEffect(() => { return () => { if (autocompleteTimer.current) clearTimeout(autocompleteTimer.current); }; }, []);

  // Load global stats on mount
  useEffect(() => {
    if (user?.zip_code) {
      return;
    }

    (async () => {
      try {
        const stored = await AsyncStorage.getItem(DEMO_SETTINGS_KEY);
        if (!stored) {
          return;
        }

        const parsed = JSON.parse(stored) as { zipCode?: string };
        if (parsed.zipCode) {
          setZipCode(parsed.zipCode);
        }
      } catch {
        // Keep the dashboard usable even if saved demo settings cannot be restored.
      }
    })();
  }, [user?.zip_code]);

  useEffect(() => {
    (async () => {
      try { setErrorStats(null); const data = await apiFetch<AlertStats>('/alerts/stats'); setStats(data); }
      catch { setErrorStats('Failed to load risk assessment data'); }
      finally { setLoadingStats(false); }
    })();
  }, []);

  const isZip = (q: string) => /^\d{5}$/.test(q.trim());

  const fetchAutocomplete = useCallback(async (text: string) => {
    if (text.length < 2 || isZip(text)) { setSuggestions([]); setShowSuggestions(false); return; }
    try {
      const data = await apiFetch<AutocompleteResult[]>(`/location/autocomplete?q=${encodeURIComponent(text)}`);
      setSuggestions(data); setShowSuggestions(data.length > 0);
    } catch { setSuggestions([]); setShowSuggestions(false); }
  }, []);

  const handleQueryChange = (text: string) => {
    setSearchQuery(text);
    if (autocompleteTimer.current) clearTimeout(autocompleteTimer.current);
    autocompleteTimer.current = setTimeout(() => fetchAutocomplete(text), 300);
  };

  const fetchLocationData = async (query: string) => {
    setErrorSearch(null); setLoadingSearch(true); setHasSearched(true);
    setSummary(null); setAlerts([]); setForecast([]); setLocationInfo(null); setIsSaved(false);

    try {
      if (!query || query.length < 2) { setErrorSearch('Please provide a valid city name or zip code.'); return; }

      const loc = await apiFetch<LocationInfo>(`/location/search?q=${encodeURIComponent(query)}`);
      setLocationInfo(loc);

      const alertsParam = loc.zip_code ? `zip_code=${loc.zip_code}` : `lat=${loc.latitude}&lon=${loc.longitude}&state=${loc.state}`;
      const alertsPromise = apiFetch<AlertItem[]>(`/location/alerts?${alertsParam}`).catch(() => []);

      const summaryPromises: [Promise<Summary | null>, Promise<Summary | null>] = loc.zip_code
        ? [
            apiFetch<Summary | null>(`/summaries/generate/local?zip_code=${loc.zip_code}`, { method: 'POST' }).catch(() => null),
            apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${loc.zip_code}`).catch(() => null),
          ]
        : [Promise.resolve(null), Promise.resolve(null)];

      const [alertsData, generatedSummary, latestSummary] = await Promise.all([alertsPromise, ...summaryPromises]);
      setSummary(generatedSummary ?? latestSummary ?? null);
      setAlerts(alertsData ?? []);
      setAnimKey(k => k + 1);

      apiFetch<ForecastPeriod[]>(`/forecast?lat=${loc.latitude}&lon=${loc.longitude}`)
        .then(periods => setForecast(periods)).catch(() => {});

      if (isLoggedIn && loc) {
        apiFetch<{ id: number; city: string; state: string }[]>('/users/destinations')
          .then(dests => { setIsSaved(dests.some(d => d.city.toLowerCase() === loc.city.toLowerCase() && d.state === loc.state)); })
          .catch(() => {});
      }
    } catch { setErrorSearch('Failed to load weather report. Please check your connection.'); }
    finally { setLoadingSearch(false); }
  };

  const handleSelectSuggestion = (s: AutocompleteResult) => {
    setSearchQuery(s.label); setSuggestions([]); setShowSuggestions(false); Keyboard.dismiss(); fetchLocationData(s.label);
  };
  const handleSearch = () => { const q = searchQuery.trim(); if (q.length >= 2) { setShowSuggestions(false); Keyboard.dismiss(); fetchLocationData(q); } };

  const handleBookmark = async () => {
    if (!isLoggedIn) { router.push('/auth/login'); return; }
    if (!locationInfo || isSaved || isSaving) return;
    setIsSaving(true);
    try {
      await apiFetch('/users/destinations', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: locationInfo.city, state: locationInfo.state, zip_code: locationInfo.zip_code, latitude: locationInfo.latitude, longitude: locationInfo.longitude }) });
      setIsSaved(true);
    } catch (err: any) { if (err?.message?.includes('409')) setIsSaved(true); }
    finally { setIsSaving(false); }
  };

  const canSearch = searchQuery.trim().length >= 2;
  const displayName = isLoggedIn ? (user?.display_name ?? 'User') : 'Guest';

  // Derive current conditions from first forecast period
  const currentCondition = forecast[0]?.weather_main ?? 'Clear';
  const currentDesc = forecast[0]?.description ?? '';
  const currentHigh = forecast[0] ? Math.round(forecast[0].high_temp) : null;
  const currentLow = forecast[0] ? Math.round(forecast[0].low_temp) : null;
  const gradient = weatherGradient(currentCondition);

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor={palette.primaryDark} />

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Image source={brandLogo} style={styles.headerLogo} resizeMode="contain" />
          <View>
            <Text style={styles.greeting}>Welcome, {displayName}</Text>
            <Text style={styles.headerSubtitle}>Stay ahead of environmental risks</Text>
          </View>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.settingsButton} onPress={() => router.push('/main/settings')} accessibilityRole="button" accessibilityLabel="Settings">
            <Ionicons name="settings-outline" size={24} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.profileButton} onPress={() => !isLoggedIn ? router.replace('/auth/login') : router.push('/main/settings')} accessibilityRole="button" accessibilityLabel={isLoggedIn ? 'Profile' : 'Log in'}>
            <Ionicons name={!isLoggedIn ? 'log-in-outline' : 'person-circle-outline'} size={28} color={palette.white} />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* ── Search Section ─────────────────────────────────────── */}
        <View style={styles.searchSection}>
          <Text style={styles.sectionTitle}>Check Location Risk</Text>
          <Text style={styles.sectionSubtitle}>
            {!isLoggedIn ? 'Enter a city name or zip code to see current weather and risk reports.' : 'Search a different city or zip code to check another area.'}
          </Text>
          <View style={styles.searchContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
              <TextInput style={styles.input} placeholder="City, State or Zip Code" placeholderTextColor={palette.textSecondary} autoCapitalize="words" autoCorrect={false} returnKeyType="search" onSubmitEditing={handleSearch} value={searchQuery} onChangeText={handleQueryChange} onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }} />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => { setSearchQuery(''); setSuggestions([]); setShowSuggestions(false); }} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
                  <Ionicons name="close-circle" size={18} color={palette.textSecondary} />
                </TouchableOpacity>
              )}
            </View>
            <TouchableOpacity style={[styles.searchButton, !canSearch && styles.searchButtonDisabled]} onPress={handleSearch} disabled={!canSearch}>
              <Ionicons name="search" size={20} color={palette.white} />
            </TouchableOpacity>
          </View>

          {showSuggestions && suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              {suggestions.map((s, i) => (
                <TouchableOpacity key={`${s.label}-${i}`} style={[styles.suggestionRow, i < suggestions.length - 1 && styles.suggestionBorder]} onPress={() => handleSelectSuggestion(s)}>
                  <Ionicons name="location-outline" size={16} color={palette.primary} style={{ marginRight: Spacing.sm }} />
                  <Text style={styles.suggestionText}>{s.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* ── Loading ────────────────────────────────────────────── */}
        {loadingSearch && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={palette.primary} />
            <Text style={styles.loadingText}>Loading weather report...</Text>
          </View>
        )}

        {/* ── Error ──────────────────────────────────────────────── */}
        {errorSearch && (
          <View style={styles.card}>
            <Text style={[styles.summaryText, { color: palette.danger }]}>{errorSearch}</Text>
            <TouchableOpacity onPress={handleSearch} style={styles.retryButton}><Text style={styles.retryText}>Retry</Text></TouchableOpacity>
          </View>
        )}

        {/* ── Weather results ────────────────────────────────────── */}
        {!loadingSearch && !errorSearch && hasSearched && locationInfo && (
          <View key={animKey}>

            {/* ▸ Apple Weather Hero Card */}
            <FadeInView delay={0}>
              <LinearGradient colors={gradient} style={styles.heroCard} start={{ x: 0, y: 0 }} end={{ x: 0.3, y: 1 }}>
                {/* Location + bookmark */}
                <View style={styles.heroHeader}>
                  <Text style={styles.heroCity}>{locationInfo.city}</Text>
                  <TouchableOpacity onPress={handleBookmark} disabled={isSaving}>
                    <Ionicons name={isSaved ? 'bookmark' : 'bookmark-outline'} size={24} color={isSaved ? '#FFD700' : 'rgba(255,255,255,0.7)'} />
                  </TouchableOpacity>
                </View>

                {/* Big temperature */}
                <View style={styles.heroTempRow}>
                  <Ionicons name={weatherIcon(currentCondition)} size={64} color="rgba(255,255,255,0.85)" style={{ marginRight: 12 }} />
                  <Text style={styles.heroTemp}>{currentHigh ?? '--'}°</Text>
                </View>

                <Text style={styles.heroCondition}>{weatherConditionText(currentCondition, currentDesc)}</Text>
                {currentHigh != null && currentLow != null && (
                  <Text style={styles.heroHighLow}>H:{currentHigh}°  L:{currentLow}°</Text>
                )}

                {/* Hourly-style summary line */}
                {forecast[0] && (
                  <View style={styles.heroMeta}>
                    <View style={styles.heroMetaItem}>
                      <Ionicons name="water-outline" size={14} color="rgba(255,255,255,0.7)" />
                      <Text style={styles.heroMetaText}>{forecast[0].humidity}%</Text>
                    </View>
                    <View style={styles.heroMetaItem}>
                      <Ionicons name="speedometer-outline" size={14} color="rgba(255,255,255,0.7)" />
                      <Text style={styles.heroMetaText}>{forecast[0].wind_mph} mph</Text>
                    </View>
                    {forecast[0].precip_chance > 0 && (
                      <View style={styles.heroMetaItem}>
                        <Ionicons name="umbrella-outline" size={14} color="rgba(255,255,255,0.7)" />
                        <Text style={styles.heroMetaText}>{forecast[0].precip_chance}%</Text>
                      </View>
                    )}
                  </View>
                )}
              </LinearGradient>
            </FadeInView>

            {/* ▸ Horizontal daily forecast (Apple Weather style) */}
            {forecast.length > 0 && (
              <FadeInView delay={120}>
                <View style={styles.forecastCard}>
                  <View style={styles.forecastCardHeader}>
                    <Ionicons name="calendar-outline" size={14} color={palette.textSecondary} />
                    <Text style={styles.forecastCardLabel}>7-DAY FORECAST</Text>
                  </View>
                  {forecast.map((period, i) => {
                    const dayLabel = i === 0 ? 'Today' : period.day_name.slice(0, 3);
                    const icon = weatherIcon(period.weather_main);
                    const high = Math.round(period.high_temp);
                    const low = Math.round(period.low_temp);

                    // Temperature bar — normalize within forecast range
                    const allHighs = forecast.map(f => f.high_temp);
                    const allLows = forecast.map(f => f.low_temp);
                    const rangeMin = Math.min(...allLows);
                    const rangeMax = Math.max(...allHighs);
                    const range = rangeMax - rangeMin || 1;
                    const barLeft = ((low - rangeMin) / range) * 100;
                    const barWidth = ((high - low) / range) * 100;

                    return (
                      <View key={i}>
                        {i > 0 && <View style={styles.forecastDivider} />}
                        <View style={styles.forecastRow}>
                          <Text style={styles.forecastDay}>{dayLabel}</Text>
                          <Ionicons name={icon} size={20} color={palette.warning} style={{ width: 28, textAlign: 'center' }} />
                          <Text style={styles.forecastLowTemp}>{low}°</Text>
                          <View style={styles.tempBarTrack}>
                            <LinearGradient
                              colors={['#4a9eff', '#ff9500']}
                              start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                              style={[styles.tempBarFill, { left: `${barLeft}%`, width: `${Math.max(barWidth, 8)}%` }]}
                            />
                          </View>
                          <Text style={styles.forecastHighTemp}>{high}°</Text>
                        </View>
                      </View>
                    );
                  })}
                </View>
              </FadeInView>
            )}

            {/* ▸ AI Summary */}
            <FadeInView delay={240}>
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={styles.cardIconBox}><Ionicons name="sparkles" size={24} color={palette.primary} /></View>
                  <Text style={styles.cardTitle}>AI Summary</Text>
                </View>
                {summary ? (
                  <View style={styles.summaryBox}>
                    <Text style={styles.summaryTitle}>{summary.title}</Text>
                    <Text style={styles.summaryText}>{summary.content}</Text>
                    <Text style={styles.summaryMeta}>Generated {new Date(summary.generated_at).toLocaleString()}{summary.model_used ? ` via ${summary.model_used}` : ''}</Text>
                  </View>
                ) : (
                  <View style={styles.summaryBox}><Text style={styles.summaryText}>No summary available yet. The backend generates summaries from active alerts.</Text></View>
                )}
              </View>
            </FadeInView>

            {/* ▸ Active Alerts */}
            <FadeInView delay={360}>
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={[styles.cardIconBox, { backgroundColor: palette.surfaceMuted }]}><Ionicons name="warning-outline" size={24} color={palette.danger} /></View>
                  <Text style={styles.cardTitle}>Recent Alerts</Text>
                </View>
                {alerts.length > 0 ? alerts.map(alert => (
                  <View key={alert.id} style={styles.alertRow}>
                    <View style={[styles.severityDot, {
                      backgroundColor: alert.severity.includes('critical') || alert.severity.includes('extreme') ? palette.danger
                        : alert.severity.includes('high') || alert.severity.includes('severe') ? palette.warning : palette.primary,
                    }]} />
                    <View style={styles.alertRowText}>
                      <Text style={styles.alertTitle}>{alert.title}</Text>
                      <Text style={styles.alertMeta}>{alert.alert_type} · {alert.severity}</Text>
                    </View>
                  </View>
                )) : (
                  <View style={styles.summaryBox}><Text style={styles.summaryText}>No active alerts for this area.</Text></View>
                )}
              </View>
            </FadeInView>
          </View>
        )}

        {/* ── Default view (before search) ───────────────────────── */}
        {!hasSearched && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <View style={[styles.cardIconBox, { backgroundColor: palette.surfaceMuted }]}><Ionicons name="warning-outline" size={24} color={palette.danger} /></View>
              <Text style={styles.cardTitle}>Risk Assessment</Text>
            </View>
            <StateView
              state={loadingStats ? 'loading' : errorStats ? 'error' : stats ? 'success' : 'empty'}
              loadingText="Loading risk data..." emptyText="No risk data available" emptyIcon="stats-chart-outline"
              errorText={errorStats || 'Failed to load risk data'}
              onRetry={() => { setLoadingStats(true); setErrorStats(null);
                (async () => { try { const data = await apiFetch<AlertStats>('/alerts/stats'); setStats(data); } catch { setErrorStats('Failed to load risk assessment data'); } finally { setLoadingStats(false); } })();
              }}
            >
              <View style={styles.statsContainer}>
                <View style={styles.statRow}><Text style={styles.statLabel}>Total Active Alerts</Text><Text style={styles.statValue}>{stats?.total}</Text></View>
                {stats && Object.entries(stats.by_severity).map(([severity, count]) => (
                  <View key={severity} style={styles.statRow}><Text style={styles.statLabel}>{severity}</Text><Text style={styles.statValue}>{count}</Text></View>
                ))}
              </View>
            </StateView>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ── Styles ───────────────────────────────────────────────────────────

function getStyles(palette: typeof Colors.light) {
  return StyleSheet.create({
    safeArea: { flex: 1, backgroundColor: palette.background },
    header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: Spacing.lg, paddingTop: SafeArea.paddingTop, paddingBottom: Spacing.md, backgroundColor: palette.primaryDark },
    headerLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
    headerLogo: { width: 40, height: 40, marginRight: Spacing.sm },
    greeting: { ...Typography.title, fontSize: 24, color: palette.white },
    headerSubtitle: { ...Typography.meta, fontSize: 14, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
    headerActions: { flexDirection: 'row', alignItems: 'center' },
    settingsButton: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center', marginRight: Spacing.sm },
    profileButton: { width: 44, height: 44, borderRadius: 22, backgroundColor: 'rgba(255,255,255,0.15)', justifyContent: 'center', alignItems: 'center' },
    scrollContent: { padding: Spacing.lg, paddingBottom: Spacing.xxl },

    // Search
    searchSection: { marginBottom: Spacing.lg },
    sectionTitle: { ...Typography.sectionLabel, color: palette.text, marginBottom: Spacing.sm },
    sectionSubtitle: { ...Typography.meta, fontSize: 14, color: palette.textSecondary, marginBottom: Spacing.md, lineHeight: 20 },
    searchContainer: { flexDirection: 'row', alignItems: 'center' },
    inputWrapper: { flex: 1, flexDirection: 'row', alignItems: 'center', backgroundColor: palette.card, borderWidth: 1, borderColor: palette.border, borderRadius: Radius.md, height: 56, paddingHorizontal: Spacing.md, marginRight: Spacing.sm, ...Shadows.card },
    inputIcon: { marginRight: Spacing.sm },
    input: { flex: 1, ...Typography.cardHeading, fontWeight: '400', color: palette.text, height: '100%' },
    searchButton: { width: 56, height: 56, backgroundColor: palette.primary, borderRadius: Radius.md, justifyContent: 'center', alignItems: 'center', ...Shadows.card },
    searchButtonDisabled: { backgroundColor: palette.textSecondary, shadowOpacity: 0, elevation: 0 },
    suggestionsContainer: { marginTop: Spacing.sm, backgroundColor: palette.card, borderRadius: Radius.sm, borderWidth: 1, borderColor: palette.border, overflow: 'hidden', ...Shadows.card },
    suggestionRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: Spacing.sm + 4, paddingHorizontal: Spacing.md },
    suggestionBorder: { borderBottomWidth: 1, borderBottomColor: palette.border },
    suggestionText: { ...Typography.body, color: palette.text, flex: 1 },

    // Loading & error
    loadingContainer: { alignItems: 'center', paddingVertical: Spacing.xxl },
    loadingText: { ...Typography.meta, color: palette.textSecondary, marginTop: Spacing.md },
    retryButton: { marginTop: Spacing.md, alignSelf: 'center', paddingVertical: Spacing.sm, paddingHorizontal: Spacing.lg, backgroundColor: palette.primary, borderRadius: Radius.md },
    retryText: { ...Typography.body, color: palette.white, fontWeight: '600' },

    // ── Apple Weather Hero ──────────────────────────────────────
    heroCard: {
      borderRadius: Radius.lg + 4,
      padding: Spacing.lg,
      marginBottom: Spacing.md + 4,
      overflow: 'hidden',
    },
    heroHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: Spacing.xs,
    },
    heroCity: {
      fontSize: 28,
      fontWeight: '300',
      color: '#fff',
      letterSpacing: 0.5,
    },
    heroTempRow: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 2,
    },
    heroTemp: {
      fontSize: 80,
      fontWeight: '200',
      color: '#fff',
      lineHeight: 88,
      letterSpacing: -2,
    },
    heroCondition: {
      fontSize: 17,
      fontWeight: '500',
      color: 'rgba(255,255,255,0.9)',
      marginBottom: 2,
    },
    heroHighLow: {
      fontSize: 17,
      fontWeight: '500',
      color: 'rgba(255,255,255,0.7)',
      marginBottom: Spacing.md,
    },
    heroMeta: {
      flexDirection: 'row',
      gap: Spacing.lg,
      paddingTop: Spacing.md,
      borderTopWidth: StyleSheet.hairlineWidth,
      borderTopColor: 'rgba(255,255,255,0.2)',
    },
    heroMetaItem: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
    },
    heroMetaText: {
      fontSize: 13,
      fontWeight: '500',
      color: 'rgba(255,255,255,0.7)',
    },

    // ── Forecast card (Apple-style daily) ────────────────────────
    forecastCard: {
      backgroundColor: palette.card,
      borderRadius: Radius.lg,
      padding: Spacing.md + 4,
      marginBottom: Spacing.md + 4,
      ...Shadows.card,
      borderWidth: 1,
      borderColor: palette.border,
    },
    forecastCardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
      marginBottom: Spacing.sm + 2,
      paddingBottom: Spacing.sm,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: palette.border,
    },
    forecastCardLabel: {
      fontSize: 12,
      fontWeight: '600',
      color: palette.textSecondary,
      letterSpacing: 0.8,
    },
    forecastRow: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: Spacing.sm + 2,
    },
    forecastDivider: {
      height: StyleSheet.hairlineWidth,
      backgroundColor: palette.border,
    },
    forecastDay: {
      width: 50,
      fontSize: 15,
      fontWeight: '600',
      color: palette.text,
    },
    forecastLowTemp: {
      width: 32,
      fontSize: 15,
      color: palette.textSecondary,
      textAlign: 'right',
      marginRight: Spacing.sm,
    },
    forecastHighTemp: {
      width: 32,
      fontSize: 15,
      fontWeight: '600',
      color: palette.text,
      textAlign: 'right',
      marginLeft: Spacing.sm,
    },
    tempBarTrack: {
      flex: 1,
      height: 5,
      borderRadius: 3,
      backgroundColor: palette.surfaceMuted,
      overflow: 'hidden',
    },
    tempBarFill: {
      position: 'absolute',
      top: 0,
      bottom: 0,
      borderRadius: 3,
    },

    // ── Generic cards ────────────────────────────────────────────
    card: { backgroundColor: palette.card, borderRadius: Radius.lg, padding: Spacing.md + 4, marginBottom: Spacing.md + 4, ...Shadows.card, borderWidth: 1, borderColor: palette.border },
    cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: Spacing.md },
    cardIconBox: { width: 48, height: 48, borderRadius: Radius.md, backgroundColor: palette.secondary, justifyContent: 'center', alignItems: 'center', marginRight: Spacing.sm },
    cardTitle: { ...Typography.subtitle, color: palette.text },
    summaryBox: { backgroundColor: palette.surfaceMuted, borderRadius: Radius.md, padding: Spacing.md },
    summaryTitle: { ...Typography.cardHeading, color: palette.text, marginBottom: Spacing.sm },
    summaryText: { ...Typography.meta, fontSize: 14, lineHeight: 20, color: palette.textSecondary },
    summaryMeta: { ...Typography.meta, color: palette.textSecondary, marginTop: Spacing.sm },

    // Alerts
    alertRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: palette.surfaceMuted, borderRadius: Radius.md, padding: Spacing.md, marginBottom: Spacing.sm },
    severityDot: { width: 12, height: 12, borderRadius: 6, marginRight: Spacing.sm },
    alertRowText: { flex: 1 },
    alertTitle: { ...Typography.body, fontWeight: '600', color: palette.text },
    alertMeta: { ...Typography.meta, fontSize: 13, color: palette.textSecondary, marginTop: 2, textTransform: 'capitalize' },

    // Stats
    statsContainer: { backgroundColor: palette.surfaceMuted, borderRadius: Radius.md, padding: Spacing.md },
    statRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: Spacing.sm, borderBottomWidth: 1, borderBottomColor: palette.border },
    statLabel: { ...Typography.meta, fontSize: 14, color: palette.textSecondary, textTransform: 'capitalize' },
    statValue: { ...Typography.meta, fontSize: 14, fontWeight: '700', color: palette.text },
  });
}
