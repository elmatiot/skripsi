<script>
  import { onMount, tick } from 'svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';
  import {
    formatRupiah,
    currentPeriode,
    periodeFromInput,
    periodeToInput
  } from '$lib/stores.js';

  let stat = null;
  let loading = true;
  let periode = currentPeriode();
  let periodeInput = periodeToInput(periode);
  let pieCanvas, barCanvas;
  let pieChart, barChart;

  async function refresh() {
    loading = true;
    try {
      stat = await api.statistik(periode);
      await tick();
      await drawCharts();
    } finally {
      loading = false;
    }
  }

  function onPeriodeChange() {
    periode = periodeFromInput(periodeInput);
    refresh();
  }

  async function drawCharts() {
    if (!stat) return;
    const { default: Chart } = await import('chart.js/auto');
    pieChart?.destroy();
    barChart?.destroy();

    if (pieCanvas) {
      pieChart = new Chart(pieCanvas, {
        type: 'doughnut',
        data: {
          labels: stat.breakdown_pengeluaran.map((b) => b.kategori_nama),
          datasets: [{
            data: stat.breakdown_pengeluaran.map((b) => Number(b.total)),
            backgroundColor: stat.breakdown_pengeluaran.map((b) => b.warna_hex || '#6366f1')
          }]
        },
        options: { plugins: { legend: { position: 'bottom' } } }
      });
    }
    if (barCanvas) {
      barChart = new Chart(barCanvas, {
        type: 'bar',
        data: {
          labels: ['Pemasukan', 'Pengeluaran'],
          datasets: [{
            data: [Number(stat.total_pemasukan), Number(stat.total_pengeluaran)],
            backgroundColor: ['#10b981', '#ef4444']
          }]
        },
        options: { plugins: { legend: { display: false } } }
      });
    }
  }

  onMount(refresh);
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white px-6 pt-12 pb-8 safe-top">
    <h1 class="text-2xl font-bold">Statistik</h1>
    <p class="text-indigo-200 text-sm">Ringkasan pemasukan vs pengeluaran</p>
    <input type="month" bind:value={periodeInput} on:change={onPeriodeChange}
      class="mt-3 bg-white/15 text-white border border-white/30 rounded-xl px-3 py-2 text-sm" />
  </div>

  <div class="px-6 -mt-4 space-y-4">
    {#if loading || !stat}
      <Loader />
    {:else}
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white rounded-2xl p-4 border border-gray-100">
          <p class="text-xs text-gray-500">Pemasukan</p>
          <p class="font-bold text-green-600">{formatRupiah(stat.total_pemasukan)}</p>
        </div>
        <div class="bg-white rounded-2xl p-4 border border-gray-100">
          <p class="text-xs text-gray-500">Pengeluaran</p>
          <p class="font-bold text-red-600">{formatRupiah(stat.total_pengeluaran)}</p>
        </div>
      </div>

      <div class="bg-white rounded-2xl p-4 border border-gray-100">
        <h3 class="font-bold text-gray-800 mb-2">Perbandingan</h3>
        <canvas bind:this={barCanvas} height="160"></canvas>
      </div>

      <div class="bg-white rounded-2xl p-4 border border-gray-100">
        <h3 class="font-bold text-gray-800 mb-2">Breakdown Pengeluaran</h3>
        {#if stat.breakdown_pengeluaran.length === 0}
          <p class="text-sm text-gray-500">Belum ada data pengeluaran.</p>
        {:else}
          <canvas bind:this={pieCanvas} height="220"></canvas>
        {/if}
      </div>
    {/if}
  </div>
</MobileShell>
