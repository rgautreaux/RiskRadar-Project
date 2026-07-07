import { Ionicons } from '@expo/vector-icons';

/**
 * Map an OpenWeatherMap-style `weather_main` string to an Ionicons glyph name.
 *
 * Used by both the hourly forecast row and the 10-day forecast list to keep the
 * weather iconography consistent across the dashboard.
 */
export function weatherIcon(main: string): keyof typeof Ionicons.glyphMap {
  const m = main.toLowerCase();
  if (m.includes('thunder')) return 'thunderstorm-outline';
  if (m.includes('drizzle') || m.includes('rain')) return 'rainy-outline';
  if (m.includes('snow')) return 'snow-outline';
  if (m.includes('cloud')) return 'cloudy-outline';
  if (m.includes('clear')) return 'sunny-outline';
  if (['mist', 'smoke', 'haze', 'fog'].some(w => m.includes(w))) return 'water-outline';
  return 'partly-sunny-outline';
}
