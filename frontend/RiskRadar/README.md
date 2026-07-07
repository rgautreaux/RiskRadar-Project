# RiskRadar — Mobile App

React Native (Expo) mobile app for the RiskRadar environmental risk monitoring system.

## Screens

| Screen | File | Description |
|--------|------|-------------|
| Home | `app/main/home.tsx` | Search by city or ZIP code, view latest AI summary |
| Weather Report | `app/main/weather-report.tsx` | Alerts, 7-day forecast, and AI summary for a location |
| Alerts | `app/(tabs)/explore.tsx` | Browse all active alerts with hazard type filters |
| Saved Destinations | `app/(tabs)/saved.tsx` | Bookmarked locations (requires login) |
| Settings | `app/main/settings.tsx` | Push notifications, location preferences |
| Login | `app/auth/login.tsx` | Email + password login |
| Register | `app/auth/registration.tsx` | Create account |

## Key Files

| File | Purpose |
|------|---------|
| `utils/api.ts` | `apiFetch()` — all API calls go through here, auto-adds JWT token |
| `contexts/auth-context.tsx` | Login/logout state, available everywhere via `useAuth()` |
| `constants/theme.ts` | Colors, spacing, typography — all design tokens |
| `constants/api.ts` | Backend URL — auto-detects your machine's IP for Expo Go |

## Running the App

```bash
npm install
npx expo start
```

Press `w` for web, or scan the QR code with Expo Go on your phone (same WiFi as your computer).

## Connecting to the Backend

The backend must be running at `http://<your-ip>:8000`. See the main [README.md](../../README.md) for backend setup.
