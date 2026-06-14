<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    ArrowLeft,
    Trash2,
    Store,
    Calendar,
    Tag,
    CreditCard,
    FileText,
    Receipt
  } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';
  import { formatRupiah, formatRupiahFull } from '$lib/stores.js';

  $: id = $page.params.id;

  let trx = null;
  let loading = true;
  let error = '';
  let deleting = false;

  async function refresh() {
    loading = true;
    error = '';
    try {
      trx = await api.getTransaksi(id);
    } catch (e) {
      error = e?.message || 'Gagal memuat transaksi';
    } finally {
      loading = false;
    }
  }

  async function hapus() {
    if (!confirm('Hapus transaksi ini? Tindakan tidak bisa dibatalkan.')) return;
    deleting = true;
    try {
      await api.deleteTransaksi(id);
      goto('/transaksi');
    } catch (e) {
      error = e?.message || 'Gagal menghapus';
    } finally {
      deleting = false;
    }
  }

  onMount(refresh);

  function metodeLabel(m) {
    const map = { tunai: 'Tunai', transfer: 'Transfer', qris: 'QRIS', kartu: 'Kartu', ewallet: 'E-Wallet' };
    return m ? (map[m] || m) : '-';
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-purple-600 text-white px-6 pt-12 pb-8 safe-top">
    <button on:click={() => history.back()} class="mb-4 inline-flex items-center gap-1 text-white/80">
      <ArrowLeft size="20" /> Kembali
    </button>
    <h1 class="text-2xl font-bold">Detail Transaksi</h1>

    {#if trx}
      <div class="mt-4">
        <p class="text-indigo-200 text-xs uppercase tracking-wide mb-1">
          {trx.tipe === 'pemasukan' ? 'Pemasukan' : 'Pengeluaran'}
        </p>
        <p class="text-3xl font-bold {trx.tipe === 'pemasukan' ? 'text-green-300' : 'text-white'}">
          {trx.tipe === 'pemasukan' ? '+' : '-'} {formatRupiahFull(trx.nominal)}
        </p>
      </div>
    {/if}
  </div>

  <div class="px-6 -mt-4 space-y-4 pb-8">
    {#if loading}
      <Loader />
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 text-sm">{error}</div>
    {:else if trx}
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 space-y-4">
        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
            <Store class="text-indigo-600" size="18" />
          </div>
          <div class="flex-1">
            <p class="text-xs text-gray-500">Merchant / Sumber</p>
            <p class="font-semibold text-gray-800">{trx.merchant || '-'}</p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
            <Calendar class="text-indigo-600" size="18" />
          </div>
          <div class="flex-1">
            <p class="text-xs text-gray-500">Tanggal</p>
            <p class="font-semibold text-gray-800">{trx.tanggal_transaksi}</p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
            <Tag class="text-indigo-600" size="18" />
          </div>
          <div class="flex-1">
            <p class="text-xs text-gray-500">Kategori</p>
            <p class="font-semibold text-gray-800">{trx.kategori || '-'}</p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
            <CreditCard class="text-indigo-600" size="18" />
          </div>
          <div class="flex-1">
            <p class="text-xs text-gray-500">Metode Bayar</p>
            <p class="font-semibold text-gray-800">{metodeLabel(trx.metode_bayar)}</p>
          </div>
        </div>

        {#if trx.deskripsi}
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
              <FileText class="text-indigo-600" size="18" />
            </div>
            <div class="flex-1">
              <p class="text-xs text-gray-500">Deskripsi</p>
              <p class="text-gray-800">{trx.deskripsi}</p>
            </div>
          </div>
        {/if}
      </div>

      {#if trx.items?.length}
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center gap-2 mb-3">
            <Receipt class="text-indigo-600" size="18" />
            <h3 class="font-bold text-gray-800">Item ({trx.items.length})</h3>
          </div>
          <ul class="divide-y divide-gray-100">
            {#each trx.items as it}
              <li class="py-3 flex justify-between items-start">
                <div class="flex-1 min-w-0 pr-2">
                  <p class="font-medium text-gray-800 truncate">{it.nama_item}</p>
                  <p class="text-xs text-gray-500">{it.qty} × {formatRupiah(it.harga_satuan)}</p>
                </div>
                <span class="font-semibold text-gray-800">{formatRupiah(Number(it.harga_satuan) * Number(it.qty))}</span>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <button on:click={hapus} disabled={deleting}
        class="w-full py-3 rounded-xl bg-red-50 text-red-600 font-semibold border border-red-200 disabled:opacity-50 inline-flex items-center justify-center gap-2">
        <Trash2 size="18" /> {deleting ? 'Menghapus...' : 'Hapus Transaksi'}
      </button>
    {/if}
  </div>
</MobileShell>
