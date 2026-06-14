<script>
  import { onMount, tick } from 'svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';
  import { formatRupiah, currentPeriode, periodeFromInput, periodeToInput } from '$lib/stores.js';

  let stat = null;
  let loading = true;
  let error = '';
  let periode = currentPeriode();
  let periodeInput = periodeToInput(periode);
  let barCanvas;
  let barChart;

  async function refresh() {
    loading = true;
    error = '';
    try {
      stat = await api.statistik(periode);
    } catch (e) {
      error = e?.message || 'Gagal memuat statistik';
    } finally {
      loading = false;
    }
    await tick();
    drawBar();
  }

  function onPeriodeChange() {
    periode = periodeFromInput(periodeInput);
    refresh();
  }

  async function drawBar() {
    if (!stat || !barCanvas) return;
    const { default: Chart } = await import('chart.js/auto');
    barChart?.destroy();
    barChart = new Chart(barCanvas, {
      type: 'bar',
      data: {
        labels: ['Pemasukan', 'Pengeluaran'],
        datasets: [{
          data: [Number(stat.total_pemasukan), Number(stat.total_pengeluaran)],
          backgroundColor: ['#10b981', '#ef4444'],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          y: {
            ticks: {
              callback: (v) => {
                if (v >= 1_000_000) return `${(v/1_000_000).toFixed(1)}M`;
                if (v >= 1_000) return `${(v/1_000).toFixed(0)}K`;
                return v;
              }
            }
          }
        }
      }
    });
  }

  $: saldo = stat ? Number(stat.total_pemasukan) - Number(stat.total_pengeluaran) : 0;
  $: totalAll = stat ? Number(stat.total_pemasukan) + Number(stat.total_pengeluaran) : 0;
  $: pctPemasukan = totalAll > 0 ? (Number(stat?.total_pemasukan) / totalAll * 100) : 50;

  onMount(refresh);
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white px-6 pt-12 pb-8 safe-top">
    <h1 class="text-2xl font-bold">Statistik</h1>
    <p class="text-indigo-200 text-sm">Perbandingan pemasukan vs pengeluaran</p>
    <input type="month" bind:value={periodeInput} on:change={onPeriodeChange}
      class="mt-3 bg-white/15 text-white border border-white/30 rounded-xl px-3 py-2 text-sm w-full" />
  </div>

  <div class="px-6 -mt-4 space-y-4 pb-8">
    {#if loading}
      <Loader />
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 text-sm">{error}</div>
    {:else if stat}
      <!-- Saldo bersih -->
      <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
        <p class="text-xs text-gray-500 mb-1">Saldo Bersih</p>
        <p class="text-3xl font-bold {saldo >= 0 ? 'text-green-600' : 'text-red-600'}">
          {saldo >= 0 ? '+' : ''}{formatRupiah(saldo)}
        </p>
      </div>

      <!-- Kartu pemasukan & pengeluaran -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-green-50 rounded-2xl p-4 border border-green-100">
          <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center mb-2">
            <span class="text-white text-xs font-bold">↓</span>
          </div>
          <p class="text-xs text-green-700 font-medium">Pemasukan</p>
          <p class="font-bold text-green-700 text-lg mt-1">{formatRupiah(stat.total_pemasukan)}</p>
        </div>
        <div class="bg-red-50 rounded-2xl p-4 border border-red-100">
          <div class="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center mb-2">
            <span class="text-white text-xs font-bold">↑</span>
          </div>
          <p class="text-xs text-red-700 font-medium">Pengeluaran</p>
          <p class="font-bold text-red-700 text-lg mt-1">{formatRupiah(stat.total_pengeluaran)}</p>
        </div>
      </div>

      <!-- Progress bar ratio -->
      {#if totalAll > 0}
        <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-500 mb-2">Proporsi bulan ini</p>
          <div class="flex rounded-full overflow-hidden h-4">
            <div class="bg-green-500 transition-all duration-500" style="width:{pctPemasukan}%"></div>
            <div class="bg-red-400 flex-1"></div>
          </div>
          <div class="flex justify-between text-xs mt-1">
            <span class="text-green-600 font-medium">{pctPemasukan.toFixed(0)}% Pemasukan</span>
            <span class="text-red-500 font-medium">{(100-pctPemasukan).toFixed(0)}% Pengeluaran</span>
          </div>
        </div>
      {/if}

      <!-- Bar chart -->
      <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
        <h3 class="font-bold text-gray-800 mb-3">Grafik Perbandingan</h3>
        <canvas bind:this={barCanvas} height="180"></canvas>
      </div>

      <!-- Breakdown pengeluaran per kategori -->
      {#if stat.breakdown_pengeluaran.length > 0}
        <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <h3 class="font-bold text-gray-800 mb-3">Detail Pengeluaran</h3>
          <ul class="space-y-3">
            {#each stat.breakdown_pengeluaran as b}
              {@const pct = stat.total_pengeluaran > 0 ? (Number(b.total)/Number(stat.total_pengeluaran)*100) : 0}
              <li>
                <div class="flex justify-between text-sm mb-1">
                  <span class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full inline-block" style="background:{b.warna_hex||'#6366f1'}"></span>
                    {b.kategori_nama}
                  </span>
                  <span class="font-semibold text-gray-800">{formatRupiah(b.total)}</span>
                </div>
                <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                    style="width:{pct}%;background:{b.warna_hex||'#6366f1'}"></div>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Breakdown pemasukan per kategori -->
      {#if stat.breakdown_pemasukan.length > 0}
        <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <h3 class="font-bold text-gray-800 mb-3">Detail Pemasukan</h3>
          <ul class="space-y-3">
            {#each stat.breakdown_pemasukan as b}
              {@const pct = stat.total_pemasukan > 0 ? (Number(b.total)/Number(stat.total_pemasukan)*100) : 0}
              <li>
                <div class="flex justify-between text-sm mb-1">
                  <span class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full inline-block" style="background:{b.warna_hex||'#10b981'}"></span>
                    {b.kategori_nama}
                  </span>
                  <span class="font-semibold text-gray-800">{formatRupiah(b.total)}</span>
                </div>
                <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full bg-green-500 rounded-full transition-all duration-500"
                    style="width:{pct}%"></div>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      {#if stat.breakdown_pengeluaran.length === 0 && stat.breakdown_pemasukan.length === 0}
        <div class="bg-white rounded-2xl p-6 text-center border border-gray-100 text-gray-500 text-sm">
          Belum ada transaksi di periode ini.
        </div>
      {/if}
    {/if}
  </div>
</MobileShell>
