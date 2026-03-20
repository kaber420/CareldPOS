import { writable } from 'svelte/store';
import { api } from './api';

export const settings = writable({
  portal_url: '',
  store_name: 'CareldPOS',
  ticket_footer: 'Conserve este ticket para recoger su equipo.',
  isLoaded: false
});

export const publicSettings = writable({});

export async function fetchPublicSettings() {
  try {
    const response = await fetch('/api/v1/settings/public');
    if (response.ok) {
      const data = await response.json();
      const settingsMap = {};
      data.forEach(s => {
        settingsMap[s.key] = s.value;
      });
      publicSettings.set(settingsMap);
      return settingsMap;
    }
  } catch (error) {
    console.error('Error fetching public settings:', error);
  }
}

export async function fetchAllSettings() {
  try {
    const data = await api.get('/settings');
    const settingsMap = {};
    data.forEach(s => {
      settingsMap[s.key] = s;
    });
    settings.set({ ...settingsMap, isLoaded: true });
    return settingsMap;
  } catch (error) {
    console.error('Error fetching all settings:', error);
  }
}

export async function updateSetting(key, value) {
  try {
    await api.put(`/settings/key/${key}`, { value });
    settings.update(s => {
      if (s[key]) {
        s[key].value = value;
      }
      return s;
    });
    // Update public settings as well if it's there
    publicSettings.update(ps => {
      if (ps.hasOwnProperty(key)) {
        ps[key] = value;
      }
      return ps;
    });
  } catch (error) {
    console.error(`Error updating setting ${key}:`, error);
    throw error;
  }
}
