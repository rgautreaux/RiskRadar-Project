import { StatusBar } from 'expo-status-bar';
import {
  Modal,
  View,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Image,
  Animated,
} from 'react-native';
import { useRouter } from 'expo-router';
import React, { useState, useRef, useEffect } from 'react';


import { ThemedText } from '@/components/themed-text';
import { PrimaryButton } from '@/components/ui/PrimaryButton';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
// Import notification panel art
const alertNotifArt = require('@/assets/icons/navigation/RiskRadar_ALERT_NotifWindow.png');

/**
 * ModalScreen presents a branded notification details surface.
 * In production, this would display detailed information about a selected alert.
 */
export default function ModalScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
    router.back();
  };

  // SD9: Animate notification panel
  const notifFadeAnim = useRef(new Animated.Value(0)).current;
  const notifSlideAnim = useRef(new Animated.Value(24)).current;
  useEffect(() => {
    Animated.timing(notifFadeAnim, {
      toValue: 1,
      duration: 220,
      delay: 120,
      useNativeDriver: true,
    }).start();
    Animated.timing(notifSlideAnim, {
      toValue: 0,
      duration: 220,
      delay: 120,
      useNativeDriver: true,
    }).start();
  }, [notifFadeAnim, notifSlideAnim]);

  return (
    <>
      <Modal
        animationType="slide"
        transparent={true}
        visible={isVisible}
        onRequestClose={handleClose}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: palette.surface }]}> 
          {/* Header with Close Button */}
          <View
            style={[
              styles.modalHeader,
              {
                backgroundColor: palette.card,
                borderBottomColor: palette.border,
              },
            ]}
          >
            <ThemedText type="title" style={styles.modalTitle}>
              Alert Details
            </ThemedText>
            <TouchableOpacity
              onPress={handleClose}
              style={[
                styles.closeButton,
                { backgroundColor: palette.surfaceMuted },
              ]}
              activeOpacity={0.7}
              accessibilityRole="button"
              accessibilityLabel="Close alert details"
            >
              <ThemedText type="meta" lightColor={palette.text} darkColor={palette.text}>
                ✕
              </ThemedText>
            </TouchableOpacity>
          </View>

          {/* Content */}
          <ScrollView
            style={styles.modalContent}
            contentContainerStyle={styles.contentContainer}
            showsVerticalScrollIndicator={false}
          >
            {/* Notification Panel Container (SD9) */}
            <Animated.View
              style={{
                opacity: notifFadeAnim,
                transform: [{ translateY: notifSlideAnim }],
              }}
            >
              <ThemedView
                surface="card"
                elevated={true}
                padding="lg"
                style={styles.notificationPanel}
              >
                {/* Alert Icon and Title */}
                <View style={styles.alertHeader}>
                  <View style={styles.alertIconArtContainer}>
                    {/* Use alertNotifArt for critical, standardNotifArt for non-critical (future-proof) */}
                    <Image
                      source={alertNotifArt}
                      style={{ width: 56, height: 56, borderRadius: Radius.md, resizeMode: 'contain' }}
                    />
                  </View>
                  <View style={styles.alertTitleContainer}>
                    <ThemedText
                      type="sectionTitle"
                      lightColor={palette.text}
                      darkColor={palette.text}
                    >
                      Air Quality Alert
                    </ThemedText>
                    <ThemedText
                      type="eyebrow"
                      lightColor={palette.danger}
                      darkColor={palette.danger}
                      style={styles.alertSeverity}
                    >
                      CRITICAL
                    </ThemedText>
                  </View>
                </View>

              {/* Alert Description */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Description
                </ThemedText>
                <ThemedText
                  type="body"
                  lightColor={palette.textSecondary}
                  darkColor={palette.textSecondary}
                  style={styles.sectionContent}
                >
                  Unhealthy air quality detected in your area. AQI levels are
                  currently at hazardous levels. Consider limiting outdoor
                  activities and wearing protective masks if you must go outside.
                </ThemedText>
              </View>

              {/* Alert Details */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Details
                </ThemedText>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Location:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    Current Location
                  </ThemedText>
                </View>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Time:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    2 hours ago
                  </ThemedText>
                </View>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Expiration:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    Until 6:00 PM
                  </ThemedText>
                </View>
              </View>

              {/* Recommendations */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Recommendations
                </ThemedText>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Limit outdoor activities
                  </ThemedText>
                </View>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Use air filtration indoors
                  </ThemedText>
                </View>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Wear N95 masks outdoors
                  </ThemedText>
                </View>
              </View>
            </ThemedView>
            </Animated.View>

            {/* Action Button */}
            <PrimaryButton label="Acknowledge" onPress={handleClose} />
          </ScrollView>
        </SafeAreaView>
      </Modal>

      <StatusBar />
    </>
  );
}

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
  },
  modalTitle: {
    flex: 1,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: Radius.button,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    flex: 1,
  },
  contentContainer: {
    padding: Spacing.md,
    flexGrow: 1,
  },
  notificationPanel: {
    marginBottom: Spacing.lg,
    borderRadius: Radius.lg,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  alertIconArtContainer: {
    width: 56,
    height: 56,
    borderRadius: Radius.md,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
    overflow: 'hidden',
  },
  alertTitleContainer: {
    flex: 1,
  },
  alertSeverity: {
    marginTop: Spacing.xs,
  },
  section: {
    marginBottom: Spacing.lg,
    paddingBottom: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.light.border,
  },
  sectionTitle: {
    marginBottom: Spacing.md,
  },
  sectionContent: {
    lineHeight: 22,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
  },
  detailValue: {
    flex: 1,
    textAlign: 'right',
  },
  recommendationItem: {
    paddingVertical: Spacing.sm,
  },
  actionButton: {
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: Radius.button,
    alignItems: 'center',
    justifyContent: 'center',
    ...Shadows.card,
  },
});
