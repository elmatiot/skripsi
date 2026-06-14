<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { User, ArrowDownRight, ArrowUpRight, Sparkles, Plus, Receipt } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { user, formatRupiah, currentPeriode } from '$lib/stores.js';
  import { api } from '$lib/api.js';

  let stat = null;
  let recent = [];
  let insights = [];
  let loading = true;
  let triggering = false;
  let errorMsg = '';

  onMount(refresh);

  async function refresh() {
    loading = true;
    errorMsg = '';
    const periode = currentPeriode();
    const [s, t, i] = await Promise.allSettled([
      api.statistik(periode),
      api.listTransaksi({ limit: 5 }),
      api.listInsight()
    ]);

    if (s.status === 'fulfilled') stat = s.value;
    else errorMsg = s.reason?.message || 'Gagal memuat statistik';

    if (t.status === 'fulfilled') recent = t.value?.items || [];
    else if (!errorMsg) errorMsg = t.reason?.message || 'Gagal memuat transaksi';

    if (i.status === 'fulfilled') insights = i.value?.slice(0, 3) ?? [];

    loading = false;
  }

  async function generateInsight() {
    triggering = true;
    try {
      await api.generateInsight();
      setTimeout(refresh, 2500);
    } finally {
      setTimeout(() => (triggering = false), 2500);
    }
  }

  function labelTransaksi(t) {
    return t.merchant || t.kategori || t.deskripsi || 'Transaksi';
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-b from-indigo-600 to-indigo-700 pb-8">
    <div class="px-6 pt-12 pb-6 safe-top">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="text-indigo-200 text-sm">Selamat Datang</p>
          <h1 class="text-white text-2xl font-bold mt-1">{$user?.nama || 'Pengguna'}</h1>
        </div>
        <button on:click={() => goto('/profil')} class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
          <User class="text-white" size="24" />
        </button>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
        <p class="text-indigo-200 text-sm mb-2">Saldo Bulan Ini</p>
        <h2 class="text-4xl font-bold mb-6 {stat && Number(stat.saldo) < 0 ? 'text-red-300' : 'text-white'}">
          {formatRupiah(stat?.saldo || 0)}
        </h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-green-500/20 backdrop-blur-sm rounded-2xl p-4 border border-green-400/30">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                <ArrowDownRight class="text-white" size="16" />
              </div>
              <span class="text-green-100 text-xs">Pemasukan</span>
            </div>
            <p class="text-white font-bold text-lg">{formatRupiah(stat?.total_pemasukan || 0)}</p>
          </div>
          <div class="bg-red-500/20 backdrop-blur-sm rounded-2xl p-4 border border-red-400/30">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center">
                <ArrowUpRight class="text-white" size="16" />
              </div>
              <span class="text-red-100 text-xs">Pengeluaran</span>
            </div>
            <p class="text-white font-bold text-lg">{formatRupiah(stat?.total_pengeluaran || 0)}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="px-6 -mt-4 space-y-6">
    {#if errorMsg}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 text-sm">{errorMsg}</div>
    {/if}
    <div class="grid grid-cols-2 gap-3">
      <button on:click={() => goto('/manual')} class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 text-left">
        <div class="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center mb-2">
          <Plus class="text-indigo-600" size="20" />
        </div>
        <p class="font-semibold text-gray-800">Catat Manual</p>
        <p class="text-xs text-gray-500">Input pemasukan / pengeluaran</p>
      </button>
      <button on:click={() => goto('/scan')} class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 text-left">
        <div class="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center mb-2">
          <Sparkles class="text-purple-600" size="20" />
        </div>
        <p class="font-semibold text-gray-800">Scan Nota</p>
        <p class="text-xs text-gray-500">OCR + AI VLM</p>
      </button>
    </div>

    <div class="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-4 border border-indigo-100">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Sparkles class="text-white" size="16" />
          </div>
          <span class="font-semibold text-gray-800">AI Insight</span>
        </div>
        <button on:click={generateInsight} disabled={triggering} class="text-xs font-medium text-indigo-600 disabled:opacity-50">
          {triggering ? 'Membuat...' : 'Generate'}
        </button>
      </div>
      {#if insights.length === 0}
        <p class="text-sm text-gray-500">Belum ada insight. Tap <b>Generate</b> untuk membuat insight dari transaksi Anda.</p>
      {:else}
        <ul class="space-y-2">
          {#each insights as ins}
            <li class="bg-white/70 rounded-xl p-3 border border-white">
              <p class="text-sm font-semibold text-indigo-900">{ins.judul}</p>
              <p class="text-xs text-gray-700 mt-1">{ins.konten}</p>
            </li>
          {/each}
        </ul>
      {/if}
    </div>

    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-bold text-gray-800">Transaksi Terbaru</h3>
        <a href="/manual" class="text-xs text-indigo-600 font-medium">Lihat semua</a>
      </div>
      {#if loading}
        <Loader />
      {:else if recent.length === 0}
        <div class="bg-white rounded-2xl p-6 text-center border border-gray-100 text-gray-500 text-sm">
          <Receipt class="mx-auto mb-2 text-gray-400" size="32" />
          Belum ada transaksi.
        </div>
      {:else}
        <ul class="space-y-2">
          {#each recent as t}
            <li class="bg-white rounded-2xl p-4 border border-gray-100 flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-800">{labelTransaksi(t)}</p>
                <p class="text-xs text-gray-500">{t.tanggal_transaksi}</p>
              </div>
              <span class="font-bold {t.tipe === 'pemasukan' ? 'text-green-600' : 'text-red-600'}">
                {t.tipe === 'pemasukan' ? '+' : '-'} {formatRupiah(t.nominal)}
              </span>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
</MobileShell>
