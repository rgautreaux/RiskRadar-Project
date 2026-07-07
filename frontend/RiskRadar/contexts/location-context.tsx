import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export interface CurrentLocation {
  zipCode: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
}

interface LocationContextValue {
  currentLocation: CurrentLocation | null;
  setCurrentLocation: (loc: CurrentLocation | null) => void;
}

const LocationContext = createContext<LocationContextValue | undefined>(undefined);

export function LocationProvider({ children }: { children: ReactNode }) {
  const [currentLocation, setCurrentLocationState] = useState<CurrentLocation | null>(null);

  const setCurrentLocation = useCallback((loc: CurrentLocation | null) => {
    setCurrentLocationState(loc);
  }, []);

  return (
    <LocationContext.Provider value={{ currentLocation, setCurrentLocation }}>
      {children}
    </LocationContext.Provider>
  );
}

export function useCurrentLocation() {
  const ctx = useContext(LocationContext);
  if (!ctx) {
    throw new Error('useCurrentLocation must be used inside a LocationProvider');
  }
  return ctx;
}
