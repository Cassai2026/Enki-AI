const DEFAULT_BACKEND_URL = 'http://192.168.1.100:8000';

export type AppEnvironment = 'dev' | 'staging' | 'prod';

function resolveEnvironment(raw?: string): AppEnvironment {
  const value = (raw ?? '').trim().toLowerCase();
  if (value === 'staging' || value === 'prod') {
    return value;
  }
  return 'dev';
}

function normalizeUrl(raw?: string): string {
  const input = (raw ?? '').trim();
  if (!input) return '';

  try {
    const candidate = /^https?:\/\//i.test(input) ? input : `http://${input}`;
    const parsed = new URL(candidate);
    return parsed.toString().replace(/\/$/, '');
  } catch {
    return '';
  }
}

const environment = resolveEnvironment(process.env.EXPO_PUBLIC_ENKI_ENV);

const fallbackByEnvironment: Record<AppEnvironment, string> = {
  dev: DEFAULT_BACKEND_URL,
  staging: '',
  prod: '',
};

const configuredByEnvironment: Partial<Record<AppEnvironment, string>> = {
  dev: normalizeUrl(process.env.EXPO_PUBLIC_ENKI_BACKEND_URL_DEV),
  staging: normalizeUrl(process.env.EXPO_PUBLIC_ENKI_BACKEND_URL_STAGING),
  prod: normalizeUrl(process.env.EXPO_PUBLIC_ENKI_BACKEND_URL_PROD),
};

const resolvedBackendUrl =
  configuredByEnvironment[environment] || fallbackByEnvironment[environment];

export const appConfig = {
  environment,
  defaultBackendUrl: resolvedBackendUrl || DEFAULT_BACKEND_URL,
  sovereignToken: (process.env.EXPO_PUBLIC_SOVEREIGN_TOKEN ?? '').trim(),
};

export function sanitizeServerUrl(raw: string): string {
  return normalizeUrl(raw);
}
