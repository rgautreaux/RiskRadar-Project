import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiFetch, setToken, removeToken, getToken } from '@/utils/api';

const GUEST_MODE_KEY = 'riskradar_guest_mode';

interface User {
  id: number;
  display_name: string | null;
  email: string | null;
  zip_code: string | null;
  latitude: number | null;
  longitude: number | null;
  alert_types: string | null;
  notify_severity: string | null;
  created_at: string;
}

interface UserPrefsUpdate {
  zip_code?: string;
  latitude?: number | null;
  longitude?: number | null;
  alert_types?: string[] | null;
  notify_severity?: string | null;
  device_token?: string | null;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  isGuest: boolean;
  isDevUserMode: boolean;
  toggleDevUserMode: () => void;
  enterGuestMode: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (displayName: string, email: string, password: string, zipCode?: string) => Promise<void>;
  savePreferences: (updates: Partial<UserPrefsUpdate>) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);
  const [isDevUserMode, setIsDevUserMode] = useState(false);

  const toggleDevUserMode = useCallback(() => {
    setIsDevUserMode((prev) => !prev);
  }, []);

  const fakeUser: User = {
    id: 999,
    display_name: 'Dev Mock User',
    email: 'dev@riskradar.local',
    zip_code: '12345',
    latitude: null,
    longitude: null,
    alert_types: null,
    notify_severity: null,
    created_at: new Date().toISOString()
  };

  // Check for existing token or guest mode on mount
  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        if (token) {
          const me = await apiFetch<User>('/users/me');
          setUser(me);
        } else {
          const guest = await AsyncStorage.getItem(GUEST_MODE_KEY);
          if (guest === 'true') setIsGuest(true);
        }
      } catch {
        // Token expired or invalid — clear it
        await removeToken();
        const guest = await AsyncStorage.getItem(GUEST_MODE_KEY);
        if (guest === 'true') setIsGuest(true);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const enterGuestMode = useCallback(async () => {
    await AsyncStorage.setItem(GUEST_MODE_KEY, 'true');
    setIsGuest(true);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiFetch<{ access_token: string; token_type: string }>(
      '/users/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      },
    );
    await setToken(data.access_token);
    const me = await apiFetch<User>('/users/me');
    setUser(me);
  }, []);

  const register = useCallback(
    async (displayName: string, email: string, password: string, zipCode?: string) => {
      await apiFetch('/users/register', {
        method: 'POST',
        body: JSON.stringify({
          display_name: displayName,
          email,
          password,
          zip_code: zipCode || undefined,
        }),
      });
      // Auto-login after registration
      await login(email, password);
    },
    [login],
  );

  const savePreferences = useCallback(async (updates: Partial<UserPrefsUpdate>) => {
    if (!user) {
      throw new Error('No authenticated user');
    }

    const updatedUser = await apiFetch<User>(`/users/${user.id}/preferences`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    setUser(updatedUser);
  }, [user]);

  const logout = useCallback(async () => {
    await removeToken();
    await AsyncStorage.removeItem(GUEST_MODE_KEY);
    setUser(null);
    setIsGuest(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: isDevUserMode ? fakeUser : user,
        isLoading,
        isLoggedIn: isDevUserMode ? true : !!user,
        isGuest,
        isDevUserMode,
        toggleDevUserMode,
        enterGuestMode,
        login,
        register,
        savePreferences,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
