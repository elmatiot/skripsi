<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { ArrowLeft, Receipt, ChevronRight } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';
  import {
    formatRupiah,
    currentPeriode,
    periodeFromInput,
    periodeToInput
  } from '$lib/stores.js';

  let items = [];
  let total = 0;
  let nextCursor = null;
  let loading = true;
  let loadingMore = false;
  let error = '';
  let tipe = '';
  let periode = currentPeriode();
  let periodeInput = periodeToInput(periode);

  function periodeRange({ tahun, bulan }) {
    const start = `${tahun}-${String(bulan).padStart(2, '0')}-01`;
    const lastDay = new Date(tahun, bulan, 0).getDate();
    const end = `${tahun}-${String(bulan).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
    return { tanggal_dari: start, tanggal_sampai: end };
  }

  async function refresh() {
    loading = true;
    error = '';
    items = [];
    nextCursor = null;
    try {
      const range = periodeRange(periode);
      const res = await api.listTransaksi({ limit: 20, tipe: tipe || undefined, ...range });
      items = res?.items || [];
      total = res?.total || 0;
      nextCursor = res?.next_cursor || null;
    } catch (e) {
      error = e?.message || 'Gagal memuat transaksi';
    } finally {
      loading = false;
    }
  }

  async function loadMore() {
    if (!nextCursor || loadingMore) return;
    loadingMore = true;
    try {
      const range = periodeRange(periode);
      const res = await api.listTransaksi({
        limit: 20,
        cursor: nextCursor,
        tipe: tipe || undefined,
        ...range
      });
      items = [...items, ...(res?.items || [])];
      nextCursor = res?.next_cursor || null;
    } finally {
      loadingMore = false;
    }
  }

  function onPeriodeChange() {
    periode = periodeFromInput(periodeInput);
    refresh();
  }

  function setTipe(t) {
    tipe = t;
    refresh();
  }

  function labelTransaksi(t) {
    return t.merchant || t.kategori || t.deskripsi || 'Transaksi';
  }

  onMount(refresh);
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white px-6 pt-12 pb-6 safe-top">
    <button on:click={() => goto('/home')} class="mb-3 inline-flex items-center gap-1 text-white/80">
      <ArrowLeft size="20" /> Kembali
    </button>
    <h1 class="text-2xl font-bold">Semua Transaksi</h1>
    <p class="text-indigo-200 text-sm">Total {total} transaksi</p>

    <div class="mt-4">
      <label class="text-indigo-200 text-xs">Periode</label>
      <input type="month" bind:value={periodeInput} on:change={onPeriodeChange}
        class="block mt-1 bg-white/15 text-white border border-white/30 rounded-xl px-3 py-2 text-sm w-full" />
    </div>

    <div class="mt-3 grid grid-cols-3 gap-2">
      <button class="py-2 rounded-xl text-sm font-medium {tipe === '' ? 'bg-white text-indigo-700' : 'bg-white/15 text-white'}"
        on:click={() => setTipe('')}>Semua</button>
      <button class="py-2 rounded-xl text-sm font-medium {tipe === 'pemasukan' ? 'bg-white text-green-700' : 'bg-white/15 text-white'}"
        on:click={() => setTipe('pemasukan')}>Pemasukan</button>
      <button class="py-2 rounded-xl text-sm font-medium {tipe === 'pengeluaran' ? 'bg-white text-red-700' : 'bg-white/15 text-white'}"
        on:click={() => setTipe('pengeluaran')}>Pengeluaran</button>
    </div>
  </div>

  <div class="px-6 -mt-4 pb-8">
    {#if loading}
      <Loader />
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 text-sm">{error}</div>
    {:else if items.length === 0}
      <div class="bg-white rounded-2xl p-8 text-center border border-gray-100 text-gray-500 text-sm">
        <Receipt class="mx-auto mb-2 text-gray-400" size="40" />
        Belum ada transaksi di periode ini.
      </div>
    {:else}
      <ul class="space-y-2">
        {#each items as t}
          <li>
            <button on:click={() => goto(`/transaksi/${t.id}`)}
              class="w-full bg-white rounded-2xl p-4 border border-gray-100 flex items-center justify-between text-left hover:bg-gray-50 transition">
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-800 truncate">{labelTransaksi(t)}</p>
                <p class="text-xs text-gray-500">{t.tanggal_transaksi} • {t.kategori || '-'}</p>
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <span class="font-bold {t.tipe === 'pemasukan' ? 'text-green-600' : 'text-red-600'}">
                  {t.tipe === 'pemasukan' ? '+' : '-'} {formatRupiah(t.nominal)}
                </span>
                <ChevronRight class="text-gray-400" size="18" />
              </div>
            </button>
          </li>
        {/each}
      </ul>

      {#if nextCursor}
        <button on:click={loadMore} disabled={loadingMore}
          class="w-full mt-4 py-3 rounded-xl bg-white border border-gray-200 text-indigo-600 font-semibold disabled:opacity-50">
          {loadingMore ? 'Memuat...' : 'Muat lebih banyak'}
        </button>
      {/if}
    {/if}
  </div>
</MobileShell>
