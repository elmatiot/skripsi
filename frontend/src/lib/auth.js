import { goto } from '$app/navigation';
import { browser } from '$app/environment';

import { api } from './api.js';
import { storageGet, storageSet, storageRemove } from './storage.js';
import { user, token } from './stores.js';

export async function hydrateAuth() {
  if (!browser) return null;
  const t = await storageGet('auth_token');
  if (!t) {
    token.set(null);
    user.set(null);
    return null;
  }
  token.set(t);
  try {
    const me = await api.me();
    user.set(me);
    return me;
  } catch {
    await logout();
    return null;
  }
}

export async function login(email, password) {
  const res = await api.login({ email, password });
  await storageSet('auth_token', res.access_token);
  token.set(res.access_token);
  user.set(res.user);
  return res.user;
}

export async function register(nama, email, password) {
  const res = await api.register({ nama, email, password });
  await storageSet('auth_token', res.access_token);
  token.set(res.access_token);
  user.set(res.user);
  return res.user;
}

export async function logout() {
  await storageRemove('auth_token');
  token.set(null);
  user.set(null);
  if (browser) await goto('/login');
}
