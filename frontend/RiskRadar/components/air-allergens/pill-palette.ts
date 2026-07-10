import { Colors } from '@/constants/theme';

type Palette = typeof Colors.light;

/**
 * Air & Allergens pill color helpers.
 *
 * AQI buckets follow the EPA scale:
 *   0–50    Good
 *   51–100  Moderate
 *   101–150 Unhealthy for Sensitive Groups (USG)
 *   151–200 Unhealthy
 *   201–300 Very Unhealthy
 *   301+    Hazardous
 *
 * Pollen buckets follow the Google Pollen categories:
 *   None, Very Low, Low, Moderate, High, Very High.
 *
 * Backgrounds use soft tinted panels (sage / cream / peach / soft-red) to stay
 * calm and premium even when surfacing elevated risk. Foregrounds use stronger
 * accent colors from the brand palette so numbers remain glanceable.
 */

export function aqiPillBg(aqi: number, palette: Palette): string {
  if (aqi <= 50) return palette.secondary; // soft sage for Good
  if (aqi <= 100) return '#FEF3C7'; // cream-amber for Moderate
  if (aqi <= 150) return '#FED7AA'; // peach for Unhealthy for Sensitive
  return '#FECACA'; // soft red for Unhealthy+
}

export function aqiPillColor(aqi: number, palette: Palette): string {
  if (aqi <= 50) return palette.success;
  if (aqi <= 100) return palette.warning;
  if (aqi <= 150) return '#B45309';
  return palette.danger;
}

export function pollenPillBg(category: string, palette: Palette): string {
  const c = category.toLowerCase();
  if (c === 'none' || c === 'very low' || c === 'low') return palette.secondary;
  if (c === 'moderate') return '#FEF3C7';
  if (c === 'high') return '#FED7AA';
  if (c === 'very high') return '#FECACA';
  return palette.surfaceMuted;
}

export function pollenPillColor(category: string, palette: Palette): string {
  const c = category.toLowerCase();
  if (c === 'none' || c === 'very low' || c === 'low') return palette.success;
  if (c === 'moderate') return palette.warning;
  if (c === 'high') return '#B45309';
  if (c === 'very high') return palette.danger;
  return palette.textSecondary;
}

// Minimal shapes — we only read these fields. Declared locally so this module
// doesn't depend on the full AirQualityData / PollenData interfaces in index.tsx.
interface AirShape {
  aqi: number;
}
interface PollenShape {
  overall: string;
}

/**
 * Returns a plain-language tip when AQI or pollen are elevated, or `null`
 * when both are within normal ranges (so the caller can hide the tip row).
 */
export function airAllergenTip(
  air: AirShape | null,
  pollen: PollenShape | null,
): string | null {
  const aqiElevated = air && air.aqi > 100;
  const pollenElevated = pollen && ['High', 'Very High'].includes(pollen.overall);

  if (aqiElevated && pollenElevated) {
    return 'Air quality and pollen levels are elevated. Consider limiting outdoor activity, especially for sensitive travelers.';
  }
  if (aqiElevated) {
    return 'Air quality is worse than usual. Those with respiratory conditions should limit prolonged outdoor exertion.';
  }
  if (pollenElevated) {
    return 'Pollen levels are elevated. Travelers with allergies may want to take precautions before heading out.';
  }
  return null;
}
