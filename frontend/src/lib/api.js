import { storageGet, storageRemove } from './storage.js';

const BASE = import.meta.env.VITE_API_BASE || '/api';

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(path, { method = 'GET', body, headers = {}, auth = true, isForm = false } = {}) {
  const h = { ...headers };
  if (!isForm) h['Content-Type'] = 'application/json';
  if (auth) {
    const token = await storageGet('auth_token');
    if (token) h['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: h,
    body: isForm ? body : body ? JSON.stringify(body) : undefined
  });

  if (res.status === 401) {
    await storageRemove('auth_token');
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login';
    }
  }

  let data = null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) data = await res.json();
  else if (res.status !== 204) data = await res.text();

  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || res.statusText || 'Request gagal';
    throw new ApiError(msg, res.status, data);
  }
  return data;
}

function periodeQS({ tahun, bulan }) {
  return `tahun=${tahun}&bulan=${bulan}`;
}

export const api = {
  // Auth
  register: (payload) => request('/auth/register', { method: 'POST', body: payload, auth: false }),
  login: (payload) => request('/auth/login', { method: 'POST', body: payload, auth: false }),
  me: () => request('/auth/me'),

  // Kategori
  listKategori: (tipe) => request(`/kategori${tipe ? `?tipe=${tipe}` : ''}`),

  // Transaksi
  listTransaksi: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString();
    return request(`/transaksi${qs ? `?${qs}` : ''}`);
  },
  createTransaksi: (body) => request('/transaksi', { method: 'POST', body }),
  getTransaksi: (id) => request(`/transaksi/${id}`),
  updateTransaksi: (id, body) => request(`/transaksi/${id}`, { method: 'PUT', body }),
  deleteTransaksi: (id) => request(`/transaksi/${id}`, { method: 'DELETE' }),

  // Nota
  analyzeNota: (file, model) => {
    const fd = new FormData();
    fd.append('file', file);
    if (model) fd.append('model', model);
    return request('/nota/analyze', { method: 'POST', body: fd, isForm: true });
  },

  // Budget — sekarang pakai tahun + bulan
  listBudget: (periode) =>
    request(`/budget${periode ? `?${periodeQS(periode)}` : ''}`),
  upsertBudget: (body) => request('/budget', { method: 'POST', body }),
  deleteBudget: (id) => request(`/budget/${id}`, { method: 'DELETE' }),
  budgetStatus: (periode) => request(`/budget/status?${periodeQS(periode)}`),
  statistik: (periode) => request(`/budget/statistik?${periodeQS(periode)}`),

  // Insight
  listInsight: () => request('/insight'),
  generateInsight: () => request('/insight/generate', { method: 'POST' }),
  markInsightRead: (id) => request(`/insight/${id}/read`, { method: 'POST' }),

  // Memory
  listMemory: () => request('/memory'),
  triggerCompressMemory: () => request('/memory/compress', { method: 'POST' }),

  // Profile
  getProfile: () => request('/profile'),
  updateProfile: (body) => request('/profile', { method: 'PUT', body })
};
