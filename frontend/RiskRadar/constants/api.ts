import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Expo dev server knows the host machine's IP — use it so physical devices work.
// Falls back to platform-specific defaults if not available.
const expoHost = Constants.expoConfig?.hostUri?.split(':')[0];

const DEV_HOST = expoHost ?? Platform.select({
  android: '10.0.2.2',
  default: 'localhost',
});

export const API_BASE_URL = `http://${DEV_HOST}:8000/api/v1`;
