import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '@/constants/api';

const TOKEN_KEY = 'riskradar_token';

export async function getToken(): Promise<string | null> {
  return AsyncStorage.getItem(TOKEN_KEY);
}

export async function setToken(token: string): Promise<void> {
  await AsyncStorage.setItem(TOKEN_KEY, token);
}

export async function removeToken(): Promise<void> {
  await AsyncStorage.removeItem(TOKEN_KEY);
}

/**
 * Wrapper around fetch that adds the API base URL and auth token.
 * Throws an error with the response body on non-2xx status.
 */
export async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = 30000,
): Promise<T> {
  const token = await getToken();

  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) ?? {}),
  };

  // Only set Content-Type for requests that have a body
  if (options.body) {
    headers['Content-Type'] = headers['Content-Type'] ?? 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
  } catch (err: any) {
    clearTimeout(timer);
    if (err?.name === 'AbortError') {
      throw new Error('Request timed out. Please check your connection.');
    }
    throw new Error('Network error. Please check your connection.');
  } finally {
    clearTimeout(timer);
  }

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(body || `Request failed with status ${res.status}`);
  }

  // Handle 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}
