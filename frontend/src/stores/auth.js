import { writable } from 'svelte/store';

// Estado de autenticación
export const user = writable(null);
export const token = writable(localStorage.getItem('token') || null);
export const isAuthenticated = writable(!!localStorage.getItem('token'));

// Loading global
export const loading = writable(false);

// Notificaciones
export const notifications = writable([]);

// Funciones de autenticación
export function setAuth(userData, authToken) {
  localStorage.setItem('token', authToken);
  token.set(authToken);
  user.set(userData);
  isAuthenticated.set(true);
}

export function clearAuth() {
  localStorage.removeItem('token');
  token.set(null);
  user.set(null);
  isAuthenticated.set(false);
  // Redirigir al login
  window.location.href = '/login';
}

// Función para agregar notificaciones
export function notify(message, type = 'info', duration = 3000) {
  const id = Date.now();
  notifications.update(n => [...n, { id, message, type }]);
  
  setTimeout(() => {
    notifications.update(n => n.filter(notif => notif.id !== id));
  }, duration);
}

export function removeNotification(id) {
  notifications.update(n => n.filter(notif => notif.id !== id));
}
