import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiFetch, setToken, removeToken, getToken } from '@/utils/api';

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

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  isDevUserMode: boolean;
  toggleDevUserMode: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (displayName: string, email: string, password: string, zipCode?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
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

  // Check for existing token on mount
  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        if (token) {
          const me = await apiFetch<User>('/users/me');
          setUser(me);
        }
      } catch {
        // Token expired or invalid — clear it
        await removeToken();
      } finally {
        setIsLoading(false);
      }
    })();
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

  const logout = useCallback(async () => {
    await removeToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: isDevUserMode ? fakeUser : user,
        isLoading,
        isLoggedIn: isDevUserMode ? true : !!user,
        isDevUserMode,
        toggleDevUserMode,
        login,
        register,
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
