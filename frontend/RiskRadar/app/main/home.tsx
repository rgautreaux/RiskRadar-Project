import { Redirect } from 'expo-router';

/**
 * Legacy route — the dashboard now lives at (tabs)/index.tsx.
 * Redirect any deep links or stale navigations to the tabs root.
 */
export default function HomeRedirect() {
  return <Redirect href="/" />;
}
