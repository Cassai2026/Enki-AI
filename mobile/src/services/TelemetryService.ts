import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEY_TELEMETRY = '@enki_mobile_telemetry_v1';
const MAX_EVENTS = 250;

export type TelemetryLevel = 'info' | 'warn' | 'error';

export interface TelemetryEvent {
  ts: string;
  level: TelemetryLevel;
  event: string;
  message: string;
  details?: Record<string, unknown>;
}

class TelemetryService {
  async log(
    level: TelemetryLevel,
    event: string,
    message: string,
    details?: Record<string, unknown>
  ): Promise<void> {
    const entry: TelemetryEvent = {
      ts: new Date().toISOString(),
      level,
      event,
      message,
      details,
    };

    try {
      const existing = await AsyncStorage.getItem(STORAGE_KEY_TELEMETRY);
      let parsed: TelemetryEvent[] = [];
      if (existing) {
        try {
          parsed = JSON.parse(existing) as TelemetryEvent[];
        } catch {
          parsed = [];
        }
      }
      parsed.push(entry);
      const bounded = parsed.slice(-MAX_EVENTS);
      await AsyncStorage.setItem(STORAGE_KEY_TELEMETRY, JSON.stringify(bounded));
    } catch (err) {
      console.warn('[TelemetryService] Failed to persist event', err);
    }
  }

  info(event: string, message: string, details?: Record<string, unknown>): Promise<void> {
    return this.log('info', event, message, details);
  }

  warn(event: string, message: string, details?: Record<string, unknown>): Promise<void> {
    return this.log('warn', event, message, details);
  }

  error(event: string, message: string, details?: Record<string, unknown>): Promise<void> {
    return this.log('error', event, message, details);
  }
}

export const telemetryService = new TelemetryService();
