import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Platform,
  StatusBar
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';

export default function WeatherReport() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const zipCode = params.zipCode || 'Unknown Location';

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#F9FAFB" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Weather Report</Text>
        <View style={{ width: 44 }} /> {/* Empty view for balance */}
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        
        {/* Main Weather Info */}
        <View style={styles.mainWeatherCard}>
          <Text style={styles.locationText}>Location: {zipCode}</Text>
          <View style={styles.tempContainer}>
            <Ionicons name="partly-sunny" size={80} color="#F59E0B" />
            <Text style={styles.temperature}>72°<Text style={styles.tempUnit}>F</Text></Text>
          </View>
          <Text style={styles.conditionText}>Partly Cloudy</Text>
          <Text style={styles.highLowText}>H: 78°  L: 64°</Text>
        </View>

        {/* Detailed Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Full Summary</Text>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryText}>
              Today will be mostly partly cloudy with a high near 78°F. Winds are expected to be light and variable throughout the day. Moving into the evening, temperatures will drop to around 64°F with increasing cloud cover. No precipitation is expected for the next 48 hours.
            </Text>
          </View>
        </View>

        {/* Extended Details */}
        <View style={styles.detailsGrid}>
          <View style={styles.detailCard}>
            <Ionicons name="water-outline" size={24} color="#3B82F6" />
            <Text style={styles.detailValue}>45%</Text>
            <Text style={styles.detailLabel}>Humidity</Text>
          </View>
          <View style={styles.detailCard}>
            <Ionicons name="leaf-outline" size={24} color="#10B981" />
            <Text style={styles.detailValue}>5 mph</Text>
            <Text style={styles.detailLabel}>Wind</Text>
          </View>
          <View style={styles.detailCard}>
            <Ionicons name="eye-outline" size={24} color="#8B5CF6" />
            <Text style={styles.detailValue}>10 mi</Text>
            <Text style={styles.detailLabel}>Visibility</Text>
          </View>
          <View style={styles.detailCard}>
            <Ionicons name="thermometer-outline" size={24} color="#EF4444" />
            <Text style={styles.detailValue}>74°</Text>
            <Text style={styles.detailLabel}>Feels Like</Text>
          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: Platform.OS === 'android' ? 16 : 0,
    paddingBottom: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
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
    color: '#111827',
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
    color: '#374151',
    marginBottom: 16,
  },
  tempContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  temperature: {
    fontSize: 84,
    fontWeight: '800',
    color: '#111827',
    marginLeft: 16,
  },
  tempUnit: {
    fontSize: 40,
    fontWeight: '600',
    color: '#6B7280',
  },
  conditionText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#4B5563',
    marginTop: 8,
  },
  highLowText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#6B7280',
    marginTop: 8,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 12,
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  summaryText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#4B5563',
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 16,
  },
  detailCard: {
    width: '47%',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  detailValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginTop: 12,
    marginBottom: 4,
  },
  detailLabel: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
});
