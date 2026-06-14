import { writable, derived } from 'svelte/store';

export const user = writable(/** @type {null | {id:number,email:string,nama:string}} */ (null));
export const token = writable(/** @type {string|null} */ (null));
export const transaksiList = writable(/** @type {any[]} */ ([]));
export const kategoriList = writable(/** @type {any[]} */ ([]));
export const budgetList = writable(/** @type {any[]} */ ([]));
export const insightList = writable(/** @type {any[]} */ ([]));

export const isAuthed = derived([token, user], ([$t, $u]) => Boolean($t && $u));

export function formatRupiah(n) {
  const v = Number(n) || 0;
  if (Math.abs(v) >= 1_000_000_000) return `Rp ${(v / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(v) >= 1_000_000) return `Rp ${(v / 1_000_000).toFixed(1)}M`;
  if (Math.abs(v) >= 1_000) return `Rp ${(v / 1_000).toFixed(1)}K`;
  return `Rp ${v.toLocaleString('id-ID')}`;
}

export function formatRupiahFull(n) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 })
    .format(Number(n) || 0);
}

export function currentPeriode(date = new Date()) {
  return { tahun: date.getFullYear(), bulan: date.getMonth() + 1 };
}

export function periodeLabel({ tahun, bulan }) {
  return `${String(bulan).padStart(2, '0')}/${tahun}`;
}

export function periodeFromInput(value) {
  // input type="month" -> "YYYY-MM"
  const [y, m] = (value || '').split('-').map(Number);
  return { tahun: y || new Date().getFullYear(), bulan: m || new Date().getMonth() + 1 };
}

export function periodeToInput({ tahun, bulan }) {
  return `${tahun}-${String(bulan).padStart(2, '0')}`;
}
