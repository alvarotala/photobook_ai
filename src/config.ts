const configuredApiUrl = process.env.EXPO_PUBLIC_API_URL?.trim().replace(/\/$/, '');

// 10.0.2.2 reaches the development computer from the standard Android emulator.
export const API_URL = configuredApiUrl || 'http://10.0.2.2:8000';
