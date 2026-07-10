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
  AccessibilityInfo,
  LayoutAnimation,
  UIManager,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, Redirect, useLocalSearchParams } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { useCurrentLocation } from '@/contexts/location-context';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';
import {
  EASE_OUT_QUART,
  EASE_OUT_EXPO,
  FadeInView,
  HeroRise,
  CountUp,
} from '@/components/motion/animations';
import { TempBar } from '@/components/weather/temp-bar';
import {
  HourlyForecastRow,
  synthesizeHourlyForecast,
} from '@/components/weather/hourly-forecast-row';
import { weatherIcon } from '@/components/weather/weather-icon';
import {
  aqiPillBg,
  aqiPillColor,
  pollenPillBg,
  pollenPillColor,
  airAllergenTip,
} from '@/components/air-allergens/pill-palette';
import { LoadingBee } from '@/components/motion/loading-bee';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface AirQualityData {
  aqi: number;
  category: string;
  pollutant: string;
  observed_at: string;
  area: string;
}

interface PollenType {
  name: string;
  category: string;
  value: number;
}

interface PollenData {
  overall: string;
  overall_value: number;
  types: PollenType[];
  observed_at: string;
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

/**
 * Short relative timestamp for meta lines like "Generated 15 min ago".
 *
 * The summary cache TTL is 1 hour, so the user almost always sees a figure in
 * minutes. Precise time beats a bare date here because freshness — not
 * calendar date — is what tells them whether to trust the briefing.
 */
function relativeTimeShort(iso: string): string {
  const d = new Date(iso);
  const diffMin = (Date.now() - d.getTime()) / 60000;
  if (diffMin < 1) return 'just now';
  if (diffMin < 60) return `${Math.round(diffMin)} min ago`;
  if (diffMin < 24 * 60) {
    const hours = Math.round(diffMin / 60);
    return `${hours} hour${hours === 1 ? '' : 's'} ago`;
  }
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export default function HomeScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { user, isLoggedIn, isGuest } = useAuth();
  const { setCurrentLocation } = useCurrentLocation();
  const params = useLocalSearchParams();
  const incomingQuery = Array.isArray(params.q) ? params.q[0] : params.q;
  const [searchQuery, setSearchQuery] = useState(user?.zip_code ?? '');
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [errorSummary, setErrorSummary] = useState<string | null>(null);

  // Air & Allergens
  const [airQuality, setAirQuality] = useState<AirQualityData | null>(null);
  const [pollen, setPollen] = useState<PollenData | null>(null);
  const [loadingAirAllergens, setLoadingAirAllergens] = useState(false);

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
  // Epoch counters guard against out-of-order async responses.
  // If user types "Houston, Te" then "Houston, Texas" fast, a slow-resolving
  // "Te" response (which returns Delaware) must NOT overwrite the newer
  // "Texas" response. Each async call captures the current epoch; if it
  // doesn't match the latest by the time it resolves, the result is dropped.
  const autocompleteEpoch = useRef(0);
  const weatherQueryEpoch = useRef(0);

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
        const myEpoch = ++autocompleteEpoch.current;
        try {
          const data = await apiFetch<AutocompleteResult[]>(
            `/location/autocomplete?q=${encodeURIComponent(text)}`
          );
          // Drop stale results — a newer keystroke has already superseded this request
          if (myEpoch !== autocompleteEpoch.current) return;
          setSuggestions(data);
          setShowSuggestions(data.length > 0);
        } catch {
          if (myEpoch !== autocompleteEpoch.current) return;
          setSuggestions([]);
          setShowSuggestions(false);
        }
      }, 300);
    } else {
      // Bump epoch so any in-flight request is abandoned
      ++autocompleteEpoch.current;
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  // Fetch weather data in-place for a given query
  const loadWeatherForQuery = async (query: string) => {
    const trimmed = query.trim();
    if (trimmed.length < 2) return;
    // Bump epoch — this call is now the authoritative one; any earlier in-flight
    // request will see its stored epoch mismatch on resolve and drop its result.
    const myEpoch = ++weatherQueryEpoch.current;
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

      // After the first async await — check we're still the current query
      if (myEpoch !== weatherQueryEpoch.current) return;

      setLocationInfo(locInfo);

      // Share the resolved location with other tabs (Alerts, etc.)
      if (locInfo && resolvedZip) {
        setCurrentLocation({
          zipCode: resolvedZip,
          city: locInfo.city,
          state: locInfo.state,
          latitude: locInfo.latitude,
          longitude: locInfo.longitude,
        });
      }

      // Kick off a location-specific AI summary refresh alongside weather/alerts
      setLoadingSummary(true);
      setErrorSummary(null);
      setLoadingAirAllergens(true);

      const [alertsData, forecastData, summaryData, aqiData, pollenData] = await Promise.all([
        resolvedZip
          ? apiFetch<AlertItem[]>(`/location/alerts?zip_code=${resolvedZip}`).catch(() => [])
          : Promise.resolve([]),
        resolvedZip
          ? apiFetch<ForecastDay[]>(`/forecast/zip?zip_code=${resolvedZip}`).catch(() => [])
          : Promise.resolve([]),
        resolvedZip
          ? apiFetch<Summary | null>(`/summaries/latest/local?zip_code=${resolvedZip}`).catch(() => null)
          : Promise.resolve(null),
        resolvedZip
          ? apiFetch<AirQualityData>(`/location/aqi?zip_code=${resolvedZip}`).catch(() => null)
          : Promise.resolve(null),
        resolvedZip
          ? apiFetch<PollenData>(`/location/pollen?zip_code=${resolvedZip}`).catch(() => null)
          : Promise.resolve(null),
      ]);

      // Final epoch check — if another query was issued while our Promise.all was in-flight, drop these results
      if (myEpoch !== weatherQueryEpoch.current) return;

      // Filter out air_quality and pollen — those have a dedicated "Air & Allergens" card.
      // Active Alerts is now reserved for real NWS severe-weather warnings.
      setAlerts(
        (alertsData ?? []).filter(
          a => a.alert_type !== 'air_quality' && a.alert_type !== 'pollen',
        ),
      );
      setForecast(forecastData ?? []);
      setSummary(summaryData); // always update — null means no alerts/summary for this area
      setSummaryExpanded(false); // collapse when location changes
      setLoadingSummary(false);
      setAirQuality(aqiData);
      setPollen(pollenData);
      setLoadingAirAllergens(false);
    } catch {
      if (myEpoch !== weatherQueryEpoch.current) return;
      setWeatherError(`Could not find location for "${trimmed}". Try a different city or zip code.`);
      setLocationInfo(null);
      setForecast([]);
      setAlerts([]);
      setAirQuality(null);
      setPollen(null);
      setLoadingSummary(false);
      setLoadingAirAllergens(false);
    } finally {
      // Only clear the loading flag if we're still the latest query — otherwise a
      // stale .finally could flicker loading off while the newer query is still fetching.
      if (myEpoch === weatherQueryEpoch.current) setLoadingWeather(false);
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

  const summaryNeedsToggle = (summary?.content?.length ?? 0) > 160;

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={palette.background} />

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
                <TouchableOpacity
                  onPress={() => { setSearchQuery(''); setSuggestions([]); setShowSuggestions(false); }}
                  activeOpacity={0.6}
                  accessibilityRole="button"
                  accessibilityLabel="Clear search"
                  hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}
                >
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
                  accessibilityRole="button"
                  accessibilityLabel={`Search for ${item.label}`}
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
              {/* Weather Hero — subtle sage-to-cream gradient backdrop, iOS-Weather-adjacent proportions.
                  Save button floats in the top-right corner so it doesn't compete with the city name for
                  visual weight in the centered headline row. */}
              <View style={styles.weatherHeroWrap}>
                <LinearGradient
                  colors={[palette.secondary, palette.surface]}
                  start={{ x: 0.5, y: 0 }}
                  end={{ x: 0.5, y: 1 }}
                  style={styles.weatherHeroBackdrop}
                  pointerEvents="none"
                />
                {locationInfo && (
                  <Animated.View style={[styles.saveButtonFloating, { transform: [{ scale: saveScale }] }]}>
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
                <HeroRise reducedMotion={reducedMotion}>
                  <FadeInView delay={80} duration={520} distance={12} reducedMotion={reducedMotion} style={styles.weatherHero}>
                    <Text style={styles.heroLocation} numberOfLines={1}>
                      {locationInfo ? `${locationInfo.city}, ${locationInfo.state}` : searchQuery}
                    </Text>
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
                          H:{Math.round(today.high_temp)}°  •  L:{Math.round(today.low_temp)}°
                        </Text>
                      </>
                    )}
                  </FadeInView>
                </HeroRise>
              </View>

              {/* Today's Briefing — pulled up right under the hero so the AI summary is the
                  second thing the user sees, matching the iOS-Weather-style "hero + briefing"
                  rhythm. Delay 180 sits just after the hero's 80ms entrance so it feels
                  deliberately chained rather than late. */}
              <FadeInView delay={180} reducedMotion={reducedMotion} style={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={styles.cardIconBox}>
                    <Ionicons name="sparkles-outline" size={22} color={palette.primary} />
                  </View>
                  <Text style={styles.cardTitle}>Today's Briefing</Text>
                </View>

                {loadingSummary ? (
                  // Flying-bee loading state. Signals "the system is working on it"
                  // without the alarm of a frantic spinner. Sits inside the
                  // summaryBox shell so the user previews where content will appear.
                  <View style={styles.summaryBox}>
                    <LoadingBee reducedMotion={reducedMotion} palette={palette} />
                  </View>
                ) : (
                  <StateView
                    state={errorSummary ? 'error' : summary ? 'success' : 'empty'}
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
                      {/*
                        Key-based remount forces React Native to drop the cached Text
                        measurement when the expanded state flips — this is the fix for
                        the Android bug where numberOfLines={undefined} failed to
                        re-expand a previously clipped <Text>. numberOfLines={0} means
                        "no limit" and is more reliable than undefined.
                      */}
                      <Text
                        key={summaryExpanded ? 'expanded' : 'collapsed'}
                        style={styles.summaryText}
                        numberOfLines={summaryExpanded ? 0 : 3}
                      >
                        {summary?.content}
                      </Text>
                      <Text style={styles.summaryMeta}>
                        {summary ? `Updated ${relativeTimeShort(summary.generated_at)}` : ''}
                      </Text>

                      {summaryNeedsToggle && (
                        <TouchableOpacity
                          style={styles.toggleButton}
                          onPress={toggleSummary}
                          activeOpacity={0.6}
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
                )}
              </FadeInView>

              {/* Today's Highlights strip — humidity / wind / precip */}
              {today && (
                <FadeInView delay={280} duration={480} reducedMotion={reducedMotion} style={styles.highlightsCard}>
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

              {/* Hourly Forecast — synthesized 8-slot row (not from a true hourly source) */}
              {today && (
                <FadeInView delay={380} duration={460} reducedMotion={reducedMotion} style={styles.forecastCard}>
                  <Text style={[styles.forecastHeader, styles.forecastHeaderTight]}>Hourly Forecast</Text>
                  <Text style={styles.forecastSubheader}>Estimated from daily range</Text>
                  <HourlyForecastRow
                    slots={synthesizeHourlyForecast(today, forecast[1])}
                    palette={palette}
                    baseDelay={300}
                    reducedMotion={reducedMotion}
                  />
                </FadeInView>
              )}

              {/* 10-Day Forecast — rows slide in, then the temp range bars animate in on top */}
              {forecast.length > 1 && (
                <FadeInView delay={500} duration={480} reducedMotion={reducedMotion} style={styles.forecastCard}>
                  <Text style={styles.forecastHeader}>{forecast.length}-Day Forecast</Text>
                  {forecast.map((day, i) => {
                    const lowFraction = (day.low_temp - tempMin) / tempSpan;
                    const highFraction = (day.high_temp - tempMin) / tempSpan;
                    // Enforce a readable minimum span so extremely narrow ranges still show a bar
                    const rawSpan = highFraction - lowFraction;
                    const endFraction = rawSpan < 0.12
                      ? Math.min(1, lowFraction + 0.12)
                      : highFraction;
                    const rowDelay = 540 + i * 45;
                    const barDelay = rowDelay + 200; // bar fills AFTER the row slides in
                    // "Today" row: draw a dot at the current (high) temp within the day's range
                    const todayMarker = i === 0 ? endFraction : undefined;
                    return (
                      <FadeInView
                        key={day.date}
                        delay={rowDelay}
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
                          <TempBar
                            startFraction={lowFraction}
                            endFraction={endFraction}
                            delay={barDelay}
                            palette={palette}
                            reducedMotion={reducedMotion}
                            todayMarker={todayMarker}
                          />
                          <Text style={styles.forecastHigh}>{Math.round(day.high_temp)}°</Text>
                        </View>
                      </FadeInView>
                    );
                  })}
                </FadeInView>
              )}

              {/* Location Alerts */}
              {alerts.length > 0 && (
                <FadeInView delay={620} duration={420} reducedMotion={reducedMotion} style={styles.card}>
                  <View style={styles.cardHeader}>
                    <View style={[styles.cardIconBox, { backgroundColor: palette.dangerSoft }]}>
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

        {/* Air & Allergens Card */}
        <FadeInView delay={700} reducedMotion={reducedMotion} style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={styles.cardIconBox}>
              <Ionicons name="leaf-outline" size={22} color={palette.primary} />
            </View>
            <Text style={styles.cardTitle}>Air & Allergens</Text>
          </View>

          {loadingAirAllergens ? (
            <View style={styles.airLoadingWrap}>
              <Text style={styles.airLoadingText}>Checking air quality…</Text>
            </View>
          ) : !airQuality && !pollen ? (
            <View style={styles.airEmptyWrap}>
              <Ionicons name="cloud-offline-outline" size={28} color={palette.textTertiary} />
              <Text style={styles.airEmptyText}>No air or pollen data for this area.</Text>
            </View>
          ) : (
            <>
              <View style={styles.airGrid}>
                {/* AQI Tile */}
                <View style={styles.airTile}>
                  <Text style={styles.airTileLabel}>Air Quality</Text>
                  {airQuality ? (
                    <>
                      <Text style={styles.airTileValue}>{airQuality.aqi}</Text>
                      <View style={[styles.airPill, { backgroundColor: aqiPillBg(airQuality.aqi, palette) }]}>
                        <Text style={[styles.airPillText, { color: aqiPillColor(airQuality.aqi, palette) }]}>
                          {airQuality.category}
                        </Text>
                      </View>
                      <Text style={styles.airTileMeta}>{airQuality.pollutant}</Text>
                    </>
                  ) : (
                    <Text style={styles.airTileUnavailable}>Unavailable</Text>
                  )}
                </View>

                {/* Pollen Tile */}
                <View style={styles.airTile}>
                  <Text style={styles.airTileLabel}>Pollen</Text>
                  {pollen ? (
                    <>
                      <Text style={styles.airTileValue}>{pollen.overall_value}<Text style={styles.airTileValueDim}>/5</Text></Text>
                      <View style={[styles.airPill, { backgroundColor: pollenPillBg(pollen.overall, palette) }]}>
                        <Text style={[styles.airPillText, { color: pollenPillColor(pollen.overall, palette) }]}>
                          {pollen.overall}
                        </Text>
                      </View>
                      <Text style={styles.airTileMeta} numberOfLines={1}>
                        {pollen.types.map(t => `${t.name}: ${t.category}`).join(' · ')}
                      </Text>
                    </>
                  ) : (
                    <Text style={styles.airTileUnavailable}>Unavailable</Text>
                  )}
                </View>
              </View>

              {/* Contextual tip — only when elevated */}
              {airAllergenTip(airQuality, pollen) && (
                <View style={styles.airTipWrap}>
                  <Ionicons name="information-circle-outline" size={16} color={palette.primary} style={{ marginTop: 1 }} />
                  <Text style={styles.airTipText}>{airAllergenTip(airQuality, pollen)}</Text>
                </View>
              )}
            </>
          )}
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
    // Wraps the hero so the gradient backdrop can bleed to the scroll container's
    // horizontal edges — the negative margins offset scrollContent's padding: 24.
    weatherHeroWrap: {
      position: 'relative',
      marginHorizontal: -24,
      paddingHorizontal: 24,
      marginBottom: 12,
      overflow: 'hidden',
    },
    weatherHeroBackdrop: {
      ...StyleSheet.absoluteFillObject,
      opacity: 0.7,
    },
    weatherHero: {
      alignItems: 'center',
      paddingTop: 12,
      paddingBottom: 28,
    },
    heroLocation: {
      fontSize: 32, fontWeight: '300',
      color: palette.text, letterSpacing: 0.2,
      textAlign: 'center',
      // Leave room on both sides so long city+state strings don't collide with
      // the absolutely-positioned save button in the top-right corner.
      paddingHorizontal: 48,
    },
    // Floats in the top-right corner of weatherHeroWrap. Pulled out of the
    // heroLocationRow so the city name can be the sole visual anchor of the
    // headline row — matches the iOS-Weather reference where secondary
    // actions live at the edges, not crowded against the headline.
    saveButtonFloating: {
      position: 'absolute',
      top: 14,
      right: 20,
      zIndex: 2,
    },
    saveButton: {
      width: 40, height: 40,
      borderRadius: 20,
      alignItems: 'center', justifyContent: 'center',
      backgroundColor: palette.card,
      // Light shadow so the button visually lifts off the sage gradient
      // without needing a border (which would feel heavy at this size).
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.08,
      shadowRadius: 4,
      elevation: 2,
    },
    heroTempRow: {
      flexDirection: 'row', alignItems: 'flex-start',
      marginTop: 4, marginBottom: 4,
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
      textTransform: 'capitalize', marginTop: 2,
    },
    heroHiLo: {
      fontSize: 15, fontWeight: '600', color: palette.text, marginTop: 8,
      letterSpacing: 0.2,
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
    // Tightens header bottom-padding when a subheader follows
    forecastHeaderTight: {
      paddingBottom: 2,
    },
    // Honesty label: hourly temps are synthesized from today's high/low, not a real hourly feed
    forecastSubheader: {
      fontSize: 10, fontWeight: '400',
      color: palette.textTertiary,
      paddingHorizontal: 16,
      paddingBottom: 8,
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

    // ── Show More / Show Less toggle — full-width bottom strip, iOS "see more" affordance ──
    toggleButton: {
      marginTop: 12,
      marginHorizontal: -16, // cancel summaryBox padding so the border spans edge-to-edge
      marginBottom: -16,
      paddingVertical: 12,
      paddingHorizontal: 16,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 6,
      borderTopWidth: 1,
      borderTopColor: palette.border,
    },
    toggleButtonText: {
      fontSize: 14, fontWeight: '600', color: palette.primary,
      letterSpacing: 0.2,
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
    // Air & Allergens card styles
    airGrid: {
      flexDirection: 'row',
      gap: 12,
    },
    airTile: {
      flex: 1,
      backgroundColor: palette.surfaceMuted,
      borderRadius: 16,
      padding: 16,
      minHeight: 130,
    },
    airTileLabel: {
      fontSize: 12,
      fontWeight: '600',
      color: palette.textSecondary,
      textTransform: 'uppercase',
      letterSpacing: 0.6,
    },
    airTileValue: {
      fontSize: 34,
      fontWeight: '300',
      color: palette.text,
      marginTop: 6,
      letterSpacing: -0.5,
    },
    airTileValueDim: {
      fontSize: 20,
      color: palette.textTertiary,
      fontWeight: '400',
    },
    airPill: {
      alignSelf: 'flex-start',
      paddingHorizontal: 10,
      paddingVertical: 3,
      borderRadius: 999,
      marginTop: 4,
    },
    airPillText: {
      fontSize: 12,
      fontWeight: '600',
    },
    airTileMeta: {
      fontSize: 11,
      color: palette.textTertiary,
      marginTop: 8,
    },
    airTileUnavailable: {
      fontSize: 14,
      color: palette.textTertiary,
      marginTop: 12,
      fontStyle: 'italic',
    },
    airLoadingWrap: {
      paddingVertical: 32,
      alignItems: 'center',
    },
    airLoadingText: {
      fontSize: 14,
      color: palette.textSecondary,
    },
    airEmptyWrap: {
      paddingVertical: 24,
      alignItems: 'center',
      gap: 8,
    },
    airEmptyText: {
      fontSize: 13,
      color: palette.textTertiary,
    },
    airTipWrap: {
      flexDirection: 'row',
      gap: 8,
      marginTop: 14,
      padding: 12,
      borderRadius: 12,
      backgroundColor: palette.secondary,
    },
    airTipText: {
      flex: 1,
      fontSize: 13,
      lineHeight: 18,
      color: palette.text,
    },
  });
}
