import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Platform,
  StatusBar,
  Animated,
  Easing,
  ViewStyle,
  AccessibilityInfo,
  LayoutAnimation,
  UIManager,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, Redirect, useLocalSearchParams } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Refined easing curves — ease-out-quart for natural deceleration
const EASE_OUT_QUART = Easing.bezier(0.25, 1, 0.5, 1);
const EASE_OUT_EXPO = Easing.bezier(0.16, 1, 0.3, 1);

interface AlertStats {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
}

interface Summary {
  id: number;
  title: string;
  content: string;
  summary_type: string;
  region: string | null;
  generated_at: string;
  model_used?: string | null;
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

interface AutocompleteResult {
  label: string;
  city: string;
  state: string;
}

interface SavedDestination {
  id: number;
  city: string;
  state: string | null;
  zip_code: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
}

const DEMO_SETTINGS_KEY = 'riskradar_demo_settings';

/** FadeInView — entrance animation (fade + subtle slide), respects reduced motion */
function FadeInView({
  delay = 0,
  duration = 450,
  distance = 18,
  children,
  style,
  reducedMotion = false,
}: {
  delay?: number;
  duration?: number;
  distance?: number;
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
  reducedMotion?: boolean;
}) {
  const opacity = useRef(new Animated.Value(reducedMotion ? 1 : 0)).current;
  const translateY = useRef(new Animated.Value(reducedMotion ? 0 : distance)).current;

  useEffect(() => {
    if (reducedMotion) return;
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, {
          toValue: 1, duration, easing: EASE_OUT_QUART, useNativeDriver: true,
        }),
        Animated.timing(translateY, {
          toValue: 0, duration, easing: EASE_OUT_QUART, useNativeDriver: true,
        }),
      ]).start();
    }, delay);
    return () => clearTimeout(timer);
  }, [delay, duration, reducedMotion, opacity, translateY]);

  return (
    <Animated.View style={[style, { opacity, transform: [{ translateY }] }]}>
      {children}
    </Animated.View>
  );
}

/** CountUp — animates a number counting up to its target value */
function CountUp({
  to,
  duration = 700,
  suffix = '',
  style,
  reducedMotion = false,
}: {
  to: number;
  duration?: number;
  suffix?: string;
  style?: any;
  reducedMotion?: boolean;
}) {
  const [value, setValue] = useState(reducedMotion ? to : 0);

  useEffect(() => {
    if (reducedMotion) {
      setValue(to);
      return;
    }
    const startVal = 0;
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const t = Math.min(1, elapsed / duration);
      // ease-out-expo
      const eased = 1 - Math.pow(2, -10 * t);
      const current = Math.round(startVal + (to - startVal) * eased);
      setValue(current);
      if (t < 1) {
        requestAnimationFrame(tick);
      } else {
        setValue(to);
      }
    };
    const raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to, duration, reducedMotion]);

  return <Text style={style}>{value}{suffix}</Text>;
}

/** Animated width bar — for the temp range in 10-day forecast */
function TempBar({
  fraction,
  delay = 0,
  palette,
  reducedMotion = false,
}: {
  fraction: number; // 0..1
  delay?: number;
  palette: typeof Colors.light | typeof Colors.dark;
  reducedMotion?: boolean;
}) {
  const progress = useRef(new Animated.Value(reducedMotion ? fraction : 0)).current;

  useEffect(() => {
    if (reducedMotion) {
      progress.setValue(fraction);
      return;
    }
    const timer = setTimeout(() => {
      Animated.timing(progress, {
        toValue: fraction,
        duration: 600,
        easing: EASE_OUT_EXPO,
        useNativeDriver: false, // width animation
      }).start();
    }, delay);
    return () => clearTimeout(timer);
  }, [fraction, delay, reducedMotion, progress]);

  const widthInterp = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={{ flex: 1, height: 4, backgroundColor: palette.border, borderRadius: 2, maxWidth: 100, overflow: 'hidden' }}>
      <Animated.View style={{ height: 4, width: widthInterp, backgroundColor: palette.primary, borderRadius: 2 }} />
    </View>
  );
}

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

export default function HomeScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { user, isLoggedIn, isGuest } = useAuth();
  const params = useLocalSearchParams();
  const incomingQuery = Array.isArray(params.q) ? params.q[0] : params.q;
  const [searchQuery, setSearchQuery] = useState(user?.zip_code ?? '');
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [errorStats, setErrorStats] = useState<string | null>(null);
  const [errorSummary, setErrorSummary] = useState<string | null>(null);

  // In-page weather state
  const [locationInfo, setLocationInfo] = useState<LocationInfo | null>(null);
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  // Saved destinations
  const [savedDestinations, setSavedDestinations] = useState<SavedDestination[]>([]);
  const [savingLocation, setSavingLocation] = useState(false);

  // Reduced motion
  const [reducedMotion, setReducedMotion] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReducedMotion);
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReducedMotion);
    return () => sub?.remove();
  }, []);

  // Chevron rotation for "Show more" toggle
  const summaryChevron = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(summaryChevron, {
      toValue: summaryExpanded ? 1 : 0,
      duration: reducedMotion ? 0 : 220,
      easing: EASE_OUT_QUART,
      useNativeDriver: true,
    }).start();
  }, [summaryExpanded, reducedMotion, summaryChevron]);
  const chevronRotate = summaryChevron.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  // Weather section fade — animates when loading a new location
  const weatherOpacity = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (loadingWeather) {
      Animated.timing(weatherOpacity, {
        toValue: 0.4, duration: 180, easing: EASE_OUT_QUART, useNativeDriver: true,
      }).start();
    } else if (forecast.length > 0 || locationInfo) {
      Animated.timing(weatherOpacity, {
        toValue: 1, duration: 380, easing: EASE_OUT_QUART, useNativeDriver: true,
      }).start();
    }
  }, [loadingWeather, forecast.length, locationInfo, weatherOpacity]);

  const shouldRedirect = !isLoggedIn && !isGuest;
  const autocompleteTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (user?.zip_code) setSearchQuery(user.zip_code);
  }, [user?.zip_code]);

  useEffect(() => {
    if (shouldRedirect || user?.zip_code) return;
    (async () => {
      try {
        const stored = await AsyncStorage.getItem(DEMO_SETTINGS_KEY);
        if (!stored) return;
        const parsed = JSON.parse(stored) as { zipCode?: string };
        if (parsed.zipCode) setSearchQuery(parsed.zipCode);
      } catch {
        // ignore
      }
    })();
  }, [user?.zip_code, shouldRedirect]);

  // Autocomplete for city names (debounced)
  const handleSearchChange = (text: string) => {
    setSearchQuery(text);
    if (autocompleteTimeout.current) clearTimeout(autocompleteTimeout.current);
    const isZip = /^\d+$/.test(text);
    if (!isZip && text.length >= 2) {
      autocompleteTimeout.current = setTimeout(async () => {
        try {
          const data = await apiFetch<AutocompleteResult[]>(
            `/location/autocomplete?q=${encodeURIComponent(text)}`
          );
          setSuggestions(data);
          setShowSuggestions(data.length > 0);
        } catch {
          setSuggestions([]);
          setShowSuggestions(false);
        }
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  // Fetch weather data in-place for a given query
  const loadWeatherForQuery = async (query: string) => {
    const trimmed = query.trim();
    if (trimmed.length < 2) return;
    setLoadingWeather(true);
    setWeatherError(null);

    try {
      let resolvedZip: string | null = null;
      let locInfo: LocationInfo | null = null;

      if (/^\d{5}$/.test(trimmed)) {
        resolvedZip = trimmed;
        locInfo = await apiFetch<LocationInfo>(`/location/info?zip_code=${trimmed}`).catch(() => null);
      } else {
        const searchResult = await apiFetch<LocationInfo>(
          `/location/search?q=${encodeURIComponent(trimmed)}`
        );
        locInfo = searchResult;
        resolvedZip = searchResult.zip_code;
      }

      setLocationInfo(locInfo);

      // Kick off a location-specific AI summary refresh alongside weather/alerts
      setLoadingSummary(true);
      setErrorSummary(null);

      const [alertsData, forecastData, summaryData] = await Promise.all([
        resolvedZip
          ? apiFetch<AlertItem[]>(`/location/alerts?zip_code=${resolvedZip}`).catch(() => [])
          : Promise.resolve([]),
        resolvedZip
          ? apiFetch<ForecastDay[]>(`/forecast/zip?zip_code=${resolvedZip}`).catch(() => [])
          : Promise.resolve([]),
        resolvedZip
          ? apiFetch<Summary | null>(`/summaries/generate/local?zip_code=${resolvedZip}`, { method: 'POST' }).catch(() => null)
          : Promise.resolve(null),
      ]);

      setAlerts(alertsData ?? []);
      setForecast(forecastData ?? []);
      setSummary(summaryData); // always update — null means no alerts/summary for this area
      setSummaryExpanded(false); // collapse when location changes
      setLoadingSummary(false);
    } catch {
      setWeatherError(`Could not find location for "${trimmed}". Try a different city or zip code.`);
      setLocationInfo(null);
      setForecast([]);
      setAlerts([]);
      setLoadingSummary(false);
    } finally {
      setLoadingWeather(false);
    }
  };

  // Fetch saved destinations so we can show filled/outline bookmark state
  const fetchSavedDestinations = async () => {
    if (!isLoggedIn) return;
    try {
      const data = await apiFetch<SavedDestination[]>('/users/destinations');
      setSavedDestinations(data ?? []);
    } catch {
      // ignore — user likely not authenticated or offline
    }
  };

  // Match current locationInfo to a saved destination (city + state)
  const currentSaved = locationInfo
    ? savedDestinations.find(
        d =>
          d.city.toLowerCase() === locationInfo.city.toLowerCase() &&
          (d.state ?? '').toLowerCase() === (locationInfo.state ?? '').toLowerCase()
      )
    : undefined;

  const saveScale = useRef(new Animated.Value(1)).current;
  const animateSavePress = () => {
    if (reducedMotion) return;
    Animated.sequence([
      Animated.timing(saveScale, { toValue: 0.82, duration: 90, easing: EASE_OUT_QUART, useNativeDriver: true }),
      Animated.timing(saveScale, { toValue: 1, duration: 180, easing: EASE_OUT_EXPO, useNativeDriver: true }),
    ]).start();
  };

  const handleToggleSave = async () => {
    if (!locationInfo) return;

    if (!isLoggedIn) {
      Alert.alert(
        'Log in to save locations',
        'Create an account or log in to save destinations and access them later.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Log In', onPress: () => router.push('/auth/login') },
        ]
      );
      return;
    }

    if (savingLocation) return;
    setSavingLocation(true);
    animateSavePress();

    try {
      if (currentSaved) {
        // Unsave
        await apiFetch(`/users/destinations/${currentSaved.id}`, { method: 'DELETE' });
        setSavedDestinations(prev => prev.filter(d => d.id !== currentSaved.id));
      } else {
        // Save
        const created = await apiFetch<SavedDestination>('/users/destinations', {
          method: 'POST',
          body: JSON.stringify({
            city: locationInfo.city,
            state: locationInfo.state,
            zip_code: locationInfo.zip_code,
            latitude: locationInfo.latitude,
            longitude: locationInfo.longitude,
          }),
        });
        setSavedDestinations(prev => [created, ...prev]);
      }
    } catch (err: any) {
      const msg = err?.message?.includes('409')
        ? 'This location is already saved.'
        : 'Could not update saved locations. Please try again.';
      Alert.alert('Oops', msg);
    } finally {
      setSavingLocation(false);
    }
  };

  const handleSearch = () => {
    const trimmed = searchQuery.trim();
    if (trimmed.length < 2) return;
    setShowSuggestions(false);
    loadWeatherForQuery(trimmed);
  };

  const selectSuggestion = (suggestion: AutocompleteResult) => {
    setSearchQuery(suggestion.label);
    setSuggestions([]);
    setShowSuggestions(false);
    loadWeatherForQuery(suggestion.label);
  };

  const toggleSummary = () => {
    // Smooth layout animation for expand/collapse
    if (!reducedMotion) {
      LayoutAnimation.configureNext({
        duration: 260,
        create: { type: 'easeInEaseOut', property: 'opacity' },
        update: { type: 'easeInEaseOut' },
      });
    }
    setSummaryExpanded(prev => !prev);
  };

  useEffect(() => {
    if (shouldRedirect) return;

    (async () => {
      try {
        setErrorStats(null);
        const data = await apiFetch<AlertStats>('/alerts/stats');
        setStats(data);
      } catch {
        setErrorStats('Failed to load risk assessment data');
      } finally { setLoadingStats(false); }
    })();

    (async () => {
      try {
        setErrorSummary(null);
        const data = await apiFetch<Summary | null>('/summaries/latest');
        setSummary(data);
      } catch {
        setErrorSummary('Failed to load latest summary');
      } finally { setLoadingSummary(false); }
    })();

    fetchSavedDestinations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shouldRedirect, isLoggedIn]);

  // Auto-load weather for the user's home zip on first render
  useEffect(() => {
    if (shouldRedirect) return;
    const initial = (user?.zip_code ?? searchQuery).trim();
    if (initial.length >= 2 && !locationInfo) {
      loadWeatherForQuery(initial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shouldRedirect, user?.zip_code]);

  // React to incoming navigation params (e.g. tapping a saved destination)
  useEffect(() => {
    if (shouldRedirect) return;
    if (!incomingQuery) return;
    const trimmed = incomingQuery.trim();
    if (trimmed.length < 2) return;
    setSearchQuery(trimmed);
    setShowSuggestions(false);
    loadWeatherForQuery(trimmed);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incomingQuery, shouldRedirect]);

  if (shouldRedirect) return <Redirect href="/welcome" />;

  const displayName = isLoggedIn ? (user?.display_name ?? 'User') : 'Guest';
  const hasWeather = forecast.length > 0 || locationInfo !== null;
  const today = forecast[0];

  // Global min/low across the 10-day window so bars are comparable
  const tempMin = forecast.length ? Math.min(...forecast.map(d => d.low_temp)) : 0;
  const tempMax = forecast.length ? Math.max(...forecast.map(d => d.high_temp)) : 0;
  const tempSpan = Math.max(1, tempMax - tempMin);

  const summaryNeedsToggle = (summary?.content?.length ?? 0) > 140;

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle={scheme === 'dark' ? 'light-content' : 'dark-content'} backgroundColor={palette.background} />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome, {displayName}</Text>
          <Text style={styles.headerSubtitle}>Stay ahead of the weather</Text>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.settingsButton}
            onPress={() => router.push('/main/settings')}
            activeOpacity={0.7}
          >
            <Ionicons name="settings-outline" size={24} color={palette.textSecondary} />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.profileButton}
            onPress={() => !isLoggedIn ? router.push('/auth/login') : router.push('/main/settings')}
            activeOpacity={0.7}
          >
            <Ionicons name={!isLoggedIn ? 'log-in-outline' : 'person-circle-outline'} size={28} color={palette.primary} />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
        {/* Search Section */}
        <FadeInView delay={0} reducedMotion={reducedMotion} style={styles.searchSection}>
          <Text style={styles.sectionTitle}>Check Location Risk</Text>
          <Text style={styles.sectionSubtitle}>
            {!isLoggedIn
              ? 'Enter a city, state, or zip code to see current weather and risk reports.'
              : 'Showing your home location. Search another city or zip code to check another area.'}
          </Text>

          <View style={styles.searchContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="City, State or Zip Code"
                placeholderTextColor={palette.textSecondary}
                keyboardType="default"
                autoCapitalize="words"
                autoCorrect={false}
                value={searchQuery}
                onChangeText={handleSearchChange}
                onSubmitEditing={handleSearch}
                returnKeyType="search"
                onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => { setSearchQuery(''); setSuggestions([]); setShowSuggestions(false); }}>
                  <Ionicons name="close-circle" size={20} color={palette.textSecondary} />
                </TouchableOpacity>
              )}
            </View>
            <TouchableOpacity
              style={[styles.searchButton, searchQuery.trim().length < 2 && styles.searchButtonDisabled]}
              onPress={handleSearch}
              disabled={searchQuery.trim().length < 2}
              activeOpacity={0.8}
            >
              <Ionicons name="search" size={20} color={palette.white} />
            </TouchableOpacity>
          </View>

          {/* Autocomplete Suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <FadeInView delay={0} duration={220} distance={-8} reducedMotion={reducedMotion} style={styles.suggestionsContainer}>
              {suggestions.map((item, idx) => (
                <TouchableOpacity
                  key={`${item.label}-${idx}`}
                  style={[
                    styles.suggestionItem,
                    idx < suggestions.length - 1 && { borderBottomWidth: 1, borderBottomColor: palette.border },
                  ]}
                  onPress={() => selectSuggestion(item)}
                  activeOpacity={0.6}
                >
                  <Ionicons name="location" size={16} color={palette.primary} style={{ marginRight: 10 }} />
                  <Text style={styles.suggestionText}>{item.label}</Text>
                </TouchableOpacity>
              ))}
            </FadeInView>
          )}
        </FadeInView>

        {/* In-page Weather Display */}
        <Animated.View style={{ opacity: weatherOpacity }}>
          {loadingWeather && !hasWeather && (
            <View style={styles.weatherPlaceholder}>
              <Text style={styles.summaryText}>Loading weather…</Text>
            </View>
          )}

          {!loadingWeather && weatherError && (
            <View style={styles.card}>
              <Text style={[styles.summaryText, { color: palette.danger }]}>{weatherError}</Text>
            </View>
          )}

          {hasWeather && (
            <>
              {/* Weather Hero */}
              <FadeInView delay={80} duration={520} distance={12} reducedMotion={reducedMotion} style={styles.weatherHero}>
                <View style={styles.heroLocationRow}>
                  <Text style={styles.heroLocation} numberOfLines={1}>
                    {locationInfo ? `${locationInfo.city}, ${locationInfo.state}` : searchQuery}
                  </Text>
                  {locationInfo && (
                    <Animated.View style={{ transform: [{ scale: saveScale }] }}>
                      <TouchableOpacity
                        style={styles.saveButton}
                        onPress={handleToggleSave}
                        disabled={savingLocation}
                        activeOpacity={0.7}
                        accessibilityRole="button"
                        accessibilityLabel={currentSaved ? 'Remove from saved locations' : 'Save this location'}
                        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                      >
                        <Ionicons
                          name={currentSaved ? 'bookmark' : 'bookmark-outline'}
                          size={22}
                          color={currentSaved ? palette.primary : palette.textSecondary}
                        />
                      </TouchableOpacity>
                    </Animated.View>
                  )}
                </View>
                {today && (
                  <>
                    <View style={styles.heroTempRow}>
                      <CountUp
                        to={Math.round(today.high_temp)}
                        style={styles.heroTemp}
                        reducedMotion={reducedMotion}
                      />
                      <Text style={styles.heroDegree}>°</Text>
                    </View>
                    <Text style={styles.heroDesc}>{today.description}</Text>
                    <Text style={styles.heroHiLo}>
                      H:{Math.round(today.high_temp)}°   L:{Math.round(today.low_temp)}°
                    </Text>
                  </>
                )}
              </FadeInView>

              {/* Today's Highlights strip — humidity / wind / precip */}
              {today && (
                <FadeInView delay={180} duration={480} reducedMotion={reducedMotion} style={styles.highlightsCard}>
                  <View style={styles.highlightItem}>
                    <Ionicons name="water-outline" size={20} color={palette.primary} />
                    <Text style={styles.highlightValue}>{today.humidity}%</Text>
                    <Text style={styles.highlightLabel}>Humidity</Text>
                  </View>
                  <View style={styles.highlightDivider} />
                  <View style={styles.highlightItem}>
                    <Ionicons name="speedometer-outline" size={20} color={palette.primary} />
                    <Text style={styles.highlightValue}>{Math.round(today.wind_mph)}<Text style={styles.highlightUnit}> mph</Text></Text>
                    <Text style={styles.highlightLabel}>Wind</Text>
                  </View>
                  <View style={styles.highlightDivider} />
                  <View style={styles.highlightItem}>
                    <Ionicons name="rainy-outline" size={20} color={palette.primary} />
                    <Text style={styles.highlightValue}>{today.precip_chance}%</Text>
                    <Text style={styles.highlightLabel}>Precip</Text>
                  </View>
                </FadeInView>
              )}

              {/* 10-Day Forecast */}
              {forecast.length > 1 && (
                <FadeInView delay={280} duration={480} reducedMotion={reducedMotion} style={styles.forecastCard}>
                  <Text style={styles.forecastHeader}>10-Day Forecast</Text>
                  {forecast.map((day, i) => {
                    const lowFraction = (day.low_temp - tempMin) / tempSpan;
                    const highFraction = (day.high_temp - tempMin) / tempSpan;
                    const barWidth = Math.max(0.12, highFraction - lowFraction);
                    const barOffset = lowFraction;
                    return (
                      <FadeInView
                        key={day.date}
                        delay={340 + i * 45}
                        duration={360}
                        distance={8}
                        reducedMotion={reducedMotion}
                      >
                        <View
                          style={[
                            styles.forecastRow,
                            i < forecast.length - 1 && { borderBottomWidth: 1, borderBottomColor: palette.border },
                          ]}
                        >
                          <Text style={[styles.forecastDay, i === 0 && { fontWeight: '700', color: palette.text }]}>
                            {i === 0 ? 'Today' : day.day_name.slice(0, 3)}
                          </Text>
                          <View style={styles.forecastIconSlot}>
                            <Ionicons name={weatherIcon(day.weather_main)} size={22} color={palette.text} />
                            {day.precip_chance > 20 && (
                              <Text style={styles.forecastPrecip}>{day.precip_chance}%</Text>
                            )}
                          </View>
                          <Text style={styles.forecastLow}>{Math.round(day.low_temp)}°</Text>
                          <View style={styles.tempTrack}>
                            <View
                              style={[
                                styles.tempRange,
                                {
                                  left: `${barOffset * 100}%`,
                                  width: `${barWidth * 100}%`,
                                  backgroundColor: palette.primary,
                                },
                              ]}
                            />
                          </View>
                          <Text style={styles.forecastHigh}>{Math.round(day.high_temp)}°</Text>
                        </View>
                      </FadeInView>
                    );
                  })}
                </FadeInView>
              )}

              {/* Location Alerts */}
              {alerts.length > 0 && (
                <FadeInView delay={420} duration={420} reducedMotion={reducedMotion} style={styles.card}>
                  <View style={styles.cardHeader}>
                    <View style={[styles.cardIconBox, { backgroundColor: '#FEE2E2' }]}>
                      <Ionicons name="warning-outline" size={22} color={palette.danger} />
                    </View>
                    <Text style={styles.cardTitle}>Active Alerts</Text>
                  </View>
                  {alerts.slice(0, 5).map((alert) => (
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
                        <Text style={styles.alertMeta}>{alert.alert_type} • {alert.severity}</Text>
                      </View>
                    </View>
                  ))}
                </FadeInView>
              )}
            </>
          )}
        </Animated.View>

        {/* Latest Summary Card with Show More/Less */}
        <FadeInView delay={520} reducedMotion={reducedMotion} style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={styles.cardIconBox}>
              <Ionicons name="sparkles-outline" size={22} color={palette.primary} />
            </View>
            <Text style={styles.cardTitle}>AI Summary</Text>
          </View>

          <StateView
            state={loadingSummary ? 'loading' : errorSummary ? 'error' : summary ? 'success' : 'empty'}
            loadingText="Loading summary..."
            emptyText="No summaries available yet"
            emptyIcon="document-outline"
            errorText={errorSummary || 'Failed to load summary'}
            onRetry={() => {
              setLoadingSummary(true);
              setErrorSummary(null);
              (async () => {
                try {
                  const data = await apiFetch<Summary | null>('/summaries/latest');
                  setSummary(data);
                } catch {
                  setErrorSummary('Failed to load latest summary');
                } finally {
                  setLoadingSummary(false);
                }
              })();
            }}
          >
            <View style={styles.summaryBox}>
              {summary?.title && <Text style={styles.summaryTitle}>{summary.title}</Text>}
              <Text
                style={styles.summaryText}
                numberOfLines={summaryExpanded ? undefined : 3}
              >
                {summary?.content}
              </Text>
              <Text style={styles.summaryMeta}>
                Generated {summary ? new Date(summary.generated_at).toLocaleDateString() : ''}
              </Text>

              {summaryNeedsToggle && (
                <TouchableOpacity
                  style={styles.toggleButton}
                  onPress={toggleSummary}
                  activeOpacity={0.7}
                  accessibilityRole="button"
                  accessibilityLabel={summaryExpanded ? 'Show less' : 'Show more'}
                >
                  <Text style={styles.toggleButtonText}>
                    {summaryExpanded ? 'Show less' : 'Show more'}
                  </Text>
                  <Animated.View style={{ transform: [{ rotate: chevronRotate }] }}>
                    <Ionicons name="chevron-down" size={16} color={palette.primary} />
                  </Animated.View>
                </TouchableOpacity>
              )}
            </View>
          </StateView>
        </FadeInView>

        {/* Risk Assessment Card */}
        <FadeInView delay={600} reducedMotion={reducedMotion} style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={[styles.cardIconBox, { backgroundColor: '#FEE2E2' }]}>
              <Ionicons name="warning-outline" size={22} color={palette.danger} />
            </View>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
          </View>

          <StateView
            state={loadingStats ? 'loading' : errorStats ? 'error' : stats ? 'success' : 'empty'}
            loadingText="Loading risk data..."
            emptyText="No risk data available"
            emptyIcon="stats-chart-outline"
            errorText={errorStats || 'Failed to load risk data'}
            onRetry={() => {
              setLoadingStats(true);
              setErrorStats(null);
              (async () => {
                try {
                  const data = await apiFetch<AlertStats>('/alerts/stats');
                  setStats(data);
                } catch {
                  setErrorStats('Failed to load risk assessment data');
                } finally {
                  setLoadingStats(false);
                }
              })();
            }}
          >
            <View style={styles.statsContainer}>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Total Active Alerts</Text>
                <Text style={styles.statValue}>{stats?.total}</Text>
              </View>
              {stats && Object.entries(stats.by_severity).map(([severity, count]) => (
                <View key={severity} style={styles.statRow}>
                  <Text style={styles.statLabel}>{severity}</Text>
                  <Text style={styles.statValue}>{count}</Text>
                </View>
              ))}
            </View>
          </StateView>
        </FadeInView>
      </ScrollView>
    </SafeAreaView>
  );
}

function getStyles(palette: typeof Colors.light | typeof Colors.dark) {
  return StyleSheet.create({
    safeArea: { flex: 1, backgroundColor: palette.background },
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
    greeting: { fontSize: 24, fontWeight: '700', color: palette.text },
    headerSubtitle: { fontSize: 14, color: palette.textSecondary, marginTop: 2 },
    headerActions: { flexDirection: 'row', alignItems: 'center' },
    settingsButton: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center', marginRight: 8 },
    profileButton: {
      width: 44, height: 44, borderRadius: 22,
      backgroundColor: palette.secondary,
      justifyContent: 'center', alignItems: 'center',
    },
    scrollContent: { padding: 24, paddingBottom: 40 },
    searchSection: { marginBottom: 28 },
    sectionTitle: { fontSize: 20, fontWeight: '700', color: palette.text, marginBottom: 8 },
    sectionSubtitle: { fontSize: 14, color: palette.textSecondary, marginBottom: 16, lineHeight: 20 },
    searchContainer: { flexDirection: 'row', alignItems: 'center' },
    inputWrapper: {
      flex: 1, flexDirection: 'row', alignItems: 'center',
      backgroundColor: palette.card,
      borderWidth: 1, borderColor: palette.border,
      borderRadius: 16, height: 56, paddingHorizontal: 16, marginRight: 12,
      shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05, shadowRadius: 2, elevation: 2,
    },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: palette.text, height: '100%' },
    searchButton: {
      width: 56, height: 56, backgroundColor: palette.primary,
      borderRadius: 16, justifyContent: 'center', alignItems: 'center',
      shadowColor: palette.primary, shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3, shadowRadius: 4.65, elevation: 8,
    },
    searchButtonDisabled: { backgroundColor: palette.textSecondary, shadowOpacity: 0, elevation: 0 },
    suggestionsContainer: {
      marginTop: 8, backgroundColor: palette.card, borderRadius: 12,
      borderWidth: 1, borderColor: palette.border,
      shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1, shadowRadius: 4, elevation: 4, overflow: 'hidden',
    },
    suggestionItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 16 },
    suggestionText: { fontSize: 15, color: palette.text },

    // ── Weather Hero (iOS Weather–inspired, but warm neutrals) ──
    weatherPlaceholder: {
      paddingVertical: 40, alignItems: 'center',
    },
    weatherHero: {
      alignItems: 'center',
      paddingTop: 8,
      paddingBottom: 28,
    },
    heroLocationRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 10,
    },
    heroLocation: {
      fontSize: 32, fontWeight: '300',
      color: palette.text, letterSpacing: 0.2,
      maxWidth: '78%',
    },
    saveButton: {
      width: 36, height: 36,
      borderRadius: 18,
      alignItems: 'center', justifyContent: 'center',
      backgroundColor: palette.surfaceMuted,
    },
    heroTempRow: {
      flexDirection: 'row', alignItems: 'flex-start',
      marginTop: 4,
    },
    heroTemp: {
      fontSize: 96, fontWeight: '100',
      color: palette.text, letterSpacing: -4,
      lineHeight: 100,
    },
    heroDegree: {
      fontSize: 56, fontWeight: '200',
      color: palette.text, lineHeight: 60, marginTop: 8,
    },
    heroDesc: {
      fontSize: 17, color: palette.textSecondary,
      textTransform: 'capitalize', marginTop: -4,
    },
    heroHiLo: {
      fontSize: 15, fontWeight: '600', color: palette.text, marginTop: 8,
    },

    // ── Today's Highlights ──
    highlightsCard: {
      flexDirection: 'row', alignItems: 'center',
      backgroundColor: palette.card, borderRadius: 20,
      paddingVertical: 18, paddingHorizontal: 8,
      marginBottom: 20,
      borderWidth: 1, borderColor: palette.border,
      shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
    },
    highlightItem: {
      flex: 1, alignItems: 'center', gap: 6,
    },
    highlightValue: {
      fontSize: 18, fontWeight: '600', color: palette.text,
    },
    highlightUnit: {
      fontSize: 13, fontWeight: '400', color: palette.textSecondary,
    },
    highlightLabel: {
      fontSize: 12, color: palette.textSecondary,
      textTransform: 'uppercase', letterSpacing: 0.6,
    },
    highlightDivider: {
      width: 1, height: 36, backgroundColor: palette.border,
    },

    // ── 10-Day Forecast ──
    forecastCard: {
      backgroundColor: palette.card, borderRadius: 20,
      paddingHorizontal: 4, paddingVertical: 6,
      marginBottom: 20,
      borderWidth: 1, borderColor: palette.border,
      shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
    },
    forecastHeader: {
      fontSize: 11, fontWeight: '700',
      color: palette.textSecondary,
      letterSpacing: 1.2,
      textTransform: 'uppercase',
      paddingHorizontal: 16,
      paddingTop: 14, paddingBottom: 8,
    },
    forecastRow: {
      flexDirection: 'row', alignItems: 'center',
      paddingVertical: 14, paddingHorizontal: 16,
      gap: 12,
    },
    forecastDay: { width: 52, fontSize: 16, fontWeight: '500', color: palette.text },
    forecastIconSlot: {
      width: 60, flexDirection: 'row', alignItems: 'center', gap: 4,
    },
    forecastPrecip: {
      fontSize: 11, color: palette.primary, fontWeight: '700',
    },
    forecastLow: {
      fontSize: 15, color: palette.textSecondary,
      width: 32, textAlign: 'right',
    },
    forecastHigh: {
      fontSize: 15, fontWeight: '600', color: palette.text,
      width: 32, textAlign: 'right',
    },
    tempTrack: {
      flex: 1, height: 5, backgroundColor: palette.surfaceMuted,
      borderRadius: 2.5, position: 'relative', overflow: 'hidden',
      maxWidth: 120,
    },
    tempRange: {
      position: 'absolute', top: 0, height: 5, borderRadius: 2.5,
    },

    // ── Cards (AI Summary, Risk Assessment, Alerts) ──
    card: {
      backgroundColor: palette.card, borderRadius: 24, padding: 20, marginBottom: 20,
      shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.05, shadowRadius: 12, elevation: 4,
      borderWidth: 1, borderColor: palette.border,
    },
    cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
    cardIconBox: {
      width: 44, height: 44, borderRadius: 14, backgroundColor: palette.secondary,
      justifyContent: 'center', alignItems: 'center', marginRight: 12,
    },
    cardTitle: { fontSize: 18, fontWeight: '700', color: palette.text },
    summaryBox: { backgroundColor: palette.surfaceMuted, borderRadius: 16, padding: 16 },
    summaryTitle: { fontSize: 16, fontWeight: '600', color: palette.text, marginBottom: 8 },
    summaryText: { fontSize: 14, lineHeight: 22, color: palette.textSecondary },
    summaryMeta: { fontSize: 12, color: palette.textSecondary, marginTop: 8 },

    // ── Show More / Show Less toggle ──
    toggleButton: {
      marginTop: 12,
      flexDirection: 'row', alignItems: 'center',
      alignSelf: 'flex-start',
      gap: 4,
      paddingVertical: 6, paddingHorizontal: 10,
      borderRadius: 8,
      backgroundColor: palette.card,
      borderWidth: 1, borderColor: palette.border,
    },
    toggleButtonText: {
      fontSize: 13, fontWeight: '600', color: palette.primary,
    },

    // ── Alert rows ──
    alertRow: {
      flexDirection: 'row', alignItems: 'center',
      paddingVertical: 10,
    },
    severityDot: { width: 10, height: 10, borderRadius: 5, marginRight: 12 },
    alertRowText: { flex: 1 },
    alertTitle: { fontSize: 14, fontWeight: '600', color: palette.text },
    alertMeta: { fontSize: 12, color: palette.textSecondary, marginTop: 2, textTransform: 'capitalize' },
    statsContainer: { backgroundColor: palette.surfaceMuted, borderRadius: 16, padding: 16 },
    statRow: {
      flexDirection: 'row', justifyContent: 'space-between',
      paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: palette.border,
    },
    statLabel: { fontSize: 14, color: palette.textSecondary, textTransform: 'capitalize' },
    statValue: { fontSize: 14, fontWeight: '700', color: palette.text },
  });
}
