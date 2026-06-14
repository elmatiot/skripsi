// Wrapper Preferences (Capacitor) -> fallback ke localStorage di web.
// Async API supaya seragam antara web & native.

let capPrefs = null;
async function loadCap() {
  if (capPrefs !== null) return capPrefs;
  try {
    const mod = await import('@capacitor/preferences');
    const { Capacitor } = await import('@capacitor/core');
    capPrefs = Capacitor?.isNativePlatform?.() ? mod.Preferences : false;
  } catch {
    capPrefs = false;
  }
  return capPrefs;
}

export async function storageGet(key) {
  const p = await loadCap();
  if (p) {
    const { value } = await p.get({ key });
    return value;
  }
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(key);
}

export async function storageSet(key, value) {
  const p = await loadCap();
  if (p) {
    await p.set({ key, value: String(value) });
    return;
  }
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(key, String(value));
}

export async function storageRemove(key) {
  const p = await loadCap();
  if (p) {
    await p.remove({ key });
    return;
  }
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(key);
}
