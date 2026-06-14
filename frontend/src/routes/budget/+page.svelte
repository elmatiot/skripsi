<script>
  import { onMount } from 'svelte';
  import { Plus, Wallet, Trash2 } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';
  import {
    formatRupiah,
    currentPeriode,
    periodeFromInput,
    periodeToInput
  } from '$lib/stores.js';

  let kategori = [];
  let statusList = [];
  let budgets = [];
  let loading = true;
  let periode = currentPeriode();
  let periodeInput = periodeToInput(periode);
  let formOpen = false;
  let formKategoriId = null;
  let formNominal = 0;
  let busy = false;

  onMount(refresh);

  async function refresh() {
    loading = true;
    try {
      [kategori, statusList, budgets] = await Promise.all([
        api.listKategori('pengeluaran'),
        api.budgetStatus(periode),
        api.listBudget(periode)
      ]);
      if (kategori.length && !formKategoriId) formKategoriId = kategori[0].id;
    } finally {
      loading = false;
    }
  }

  function onPeriodeChange() {
    periode = periodeFromInput(periodeInput);
    refresh();
  }

  async function saveBudget() {
    busy = true;
    try {
      await api.upsertBudget({
        kategori_id: formKategoriId,
        nominal_budget: Number(formNominal),
        tahun: periode.tahun,
        bulan: periode.bulan
      });
      formOpen = false;
      formNominal = 0;
      await refresh();
    } finally {
      busy = false;
    }
  }

  async function removeBudget(id) {
    if (!id) return;
    if (!confirm('Hapus budget ini?')) return;
    await api.deleteBudget(id);
    await refresh();
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white px-6 pt-12 pb-8 safe-top">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Budget</h1>
        <p class="text-indigo-200 text-sm">Atur batas pengeluaran per kategori</p>
      </div>
      <button on:click={() => (formOpen = !formOpen)} class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
        <Plus class="text-white" size="22" />
      </button>
    </div>

    <div class="mt-4">
      <label class="text-indigo-200 text-xs">Periode</label>
      <input type="month" bind:value={periodeInput} on:change={onPeriodeChange}
        class="block mt-1 bg-white/15 text-white border border-white/30 rounded-xl px-3 py-2 text-sm" />
    </div>
  </div>

  <div class="px-6 -mt-4 space-y-4">
    {#if formOpen}
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 space-y-3">
        <h3 class="font-bold text-gray-800">Set Budget</h3>
        <select bind:value={formKategoriId} class="w-full px-3 py-2 border rounded-lg">
          {#each kategori as k}<option value={k.id}>{k.nama}</option>{/each}
        </select>
        <input type="number" min="0" bind:value={formNominal} placeholder="Nominal (Rp)"
          class="w-full px-3 py-2 border rounded-lg" />
        <div class="flex gap-2">
          <button on:click={saveBudget} disabled={busy}
            class="flex-1 py-2 rounded-lg bg-indigo-600 text-white font-semibold disabled:opacity-50">Simpan</button>
          <button on:click={() => (formOpen = false)} class="flex-1 py-2 rounded-lg bg-gray-100">Batal</button>
        </div>
      </div>
    {/if}

    {#if loading}
      <Loader />
    {:else if statusList.length === 0}
      <div class="bg-white rounded-2xl p-6 text-center border border-gray-100">
        <Wallet class="mx-auto mb-2 text-gray-400" size="32" />
        <p class="text-sm text-gray-500">Belum ada budget di {periode.bulan}/{periode.tahun}.</p>
      </div>
    {:else}
      <ul class="space-y-3">
        {#each statusList as s}
          {@const overflow = s.persen >= 100}
          {@const warn = s.persen >= 75 && !overflow}
          <li class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-800">{s.kategori_nama}</p>
                <p class="text-xs text-gray-500">
                  Terpakai {formatRupiah(s.terpakai)} dari {formatRupiah(s.nominal_budget)}
                </p>
              </div>
              <button on:click={() => removeBudget(budgets.find((b) => b.kategori_id === s.kategori_id)?.id)} class="text-red-500"><Trash2 size="16" /></button>
            </div>
            <div class="mt-3 h-2 w-full bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full transition-all"
                style="width: {Math.min(100, s.persen)}%; background-color: {overflow ? '#ef4444' : warn ? '#f59e0b' : (s.kategori_warna || '#6366f1')};"></div>
            </div>
            <p class="text-xs mt-1 {overflow ? 'text-red-600' : warn ? 'text-amber-600' : 'text-gray-500'}">
              {s.persen}% terpakai
              {#if overflow} • melebihi budget!{/if}
            </p>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</MobileShell>
