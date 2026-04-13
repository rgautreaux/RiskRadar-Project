import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TouchableOpacity,
  StatusBar,
  Image,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useFocusEffect } from 'expo-router';
import { Colors, Spacing, Radius, Shadows, Typography, SafeArea } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

interface SavedDestination {
  id: number;
  city: string;
  state: string | null;
  zip_code: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
}

export default function SavedScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { isLoggedIn } = useAuth();

  const [destinations, setDestinations] = useState<SavedDestination[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDestinations = useCallback(async () => {
    if (!isLoggedIn) { setLoading(false); return; }
    try {
      const data = await apiFetch<SavedDestination[]>('/users/destinations');
      setDestinations(data);
    } catch {
      // Not logged in or network error
    } finally {
      setLoading(false);
    }
  }, [isLoggedIn]);

  // Refresh every time the tab is focused
  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchDestinations();
    }, [fetchDestinations])
  );

  const handleDelete = async (id: number) => {
    try {
      await apiFetch(`/users/destinations/${id}`, { method: 'DELETE' });
      setDestinations((prev) => prev.filter((d) => d.id !== id));
    } catch {
      // ignore
    }
  };

  if (!isLoggedIn) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="dark-content" backgroundColor={palette.background} />
        <View style={styles.emptyContainer}>
          <Ionicons name="bookmark-outline" size={64} color={palette.textSecondary} />
          <Text style={styles.emptyTitle}>Save Your Destinations</Text>
          <Text style={styles.emptySubtitle}>Log in to save and quickly access your favorite travel destinations.</Text>
          <TouchableOpacity
            style={styles.loginButton}
            onPress={() => router.push('/auth/login')}
            accessibilityRole="button"
            accessibilityLabel="Log in"
          >
            <Text style={styles.loginButtonText}>Log In</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={palette.background} />

      <View style={styles.header}>
        <Image source={brandLogo} style={styles.headerLogo} resizeMode="contain" />
        <Text style={styles.headerTitle}>Saved Destinations</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color={palette.primary} style={{ paddingVertical: 40 }} />
      ) : destinations.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="bookmark-outline" size={64} color={palette.textSecondary} />
          <Text style={styles.emptyTitle}>No Saved Destinations</Text>
          <Text style={styles.emptySubtitle}>Search for a city and tap the bookmark icon to save it here.</Text>
        </View>
      ) : (
        <FlatList
          data={destinations}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.card}
              onPress={() =>
                router.push({
                  pathname: '/main/weather-report',
                  params: { query: `${item.city}, ${item.state}` },
                })
              }
              accessibilityRole="button"
              accessibilityLabel={`View weather for ${item.city}${item.state ? `, ${item.state}` : ''}`}
            >
              <View style={styles.cardLeft}>
                <Ionicons name="location" size={24} color={palette.primary} />
                <View style={styles.cardText}>
                  <Text style={styles.cardCity}>
                    {item.city}{item.state ? `, ${item.state}` : ''}
                  </Text>
                  {item.zip_code && (
                    <Text style={styles.cardZip}>{item.zip_code}</Text>
                  )}
                </View>
              </View>
              <TouchableOpacity
                style={styles.deleteButton}
                onPress={() => handleDelete(item.id)}
                accessibilityRole="button"
                accessibilityLabel={`Remove ${item.city}`}
              >
                <Ionicons name="trash-outline" size={20} color={palette.danger} />
              </TouchableOpacity>
            </TouchableOpacity>
          )}
        />
      )}
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
      paddingHorizontal: Spacing.lg,
      paddingTop: SafeArea.paddingTop,
      paddingBottom: Spacing.md,
      backgroundColor: palette.card,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    headerLogo: {
      width: 32,
      height: 32,
      marginRight: Spacing.sm,
    },
    headerTitle: {
      ...Typography.title,
      fontSize: 24,
      color: palette.text,
    },
    listContent: {
      padding: Spacing.lg,
      paddingBottom: Spacing.xxl,
    },
    card: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: palette.card,
      borderRadius: Radius.md,
      padding: Spacing.md,
      marginBottom: Spacing.sm,
      borderWidth: 1,
      borderColor: palette.border,
      ...Shadows.card,
    },
    cardLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    cardText: {
      marginLeft: Spacing.sm,
      flex: 1,
    },
    cardCity: {
      ...Typography.cardHeading,
      color: palette.text,
    },
    cardZip: {
      ...Typography.meta,
      fontSize: 13,
      color: palette.textSecondary,
      marginTop: 2,
    },
    deleteButton: {
      width: 44,
      height: 44,
      justifyContent: 'center',
      alignItems: 'center',
    },
    emptyContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: Spacing.xxl,
    },
    emptyTitle: {
      ...Typography.sectionLabel,
      color: palette.text,
      marginTop: Spacing.md,
      marginBottom: Spacing.sm,
    },
    emptySubtitle: {
      ...Typography.meta,
      fontSize: 14,
      color: palette.textSecondary,
      textAlign: 'center',
      lineHeight: 20,
    },
    loginButton: {
      marginTop: Spacing.lg,
      backgroundColor: palette.primary,
      paddingHorizontal: Spacing.xl,
      paddingVertical: 14,
      borderRadius: Radius.md,
    },
    loginButtonText: {
      color: palette.white,
      ...Typography.cardHeading,
      fontWeight: '700',
    },
  });
}
