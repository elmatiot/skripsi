<script>
  import { onMount, onDestroy } from 'svelte';
  import { Sparkles, RefreshCcw, BookmarkCheck } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import Loader from '$lib/components/Loader.svelte';
  import { api } from '$lib/api.js';

  let insights = [];
  let loading = true;
  let busy = false;
  let errorMsg = '';
  let es;

  async function refresh() {
    loading = true;
    errorMsg = '';
    try {
      insights = await api.listInsight();
    } catch (e) {
      errorMsg = e?.message || 'Gagal memuat insight';
    } finally {
      loading = false;
    }
  }

  async function generate() {
    busy = true;
    errorMsg = '';
    try {
      await api.generateInsight();
      setTimeout(refresh, 2500);
    } catch (e) {
      errorMsg = e?.message || 'Gagal generate insight';
    } finally {
      setTimeout(() => (busy = false), 2500);
    }
  }

  async function markRead(id) {
    await api.markInsightRead(id);
    insights = insights.map((i) => (i.id === id ? { ...i, sudah_dibaca: true } : i));
  }

  onMount(() => {
    refresh();
    // SSE realtime — kredensial via token query? Sederhana: pakai cookie sesi nginx-side jika ada.
    try {
      es = new EventSource('/api/insight/stream');
      es.addEventListener('insight', () => refresh());
    } catch {}
  });

  onDestroy(() => es?.close?.());
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-purple-600 to-indigo-700 text-white px-6 pt-12 pb-8 safe-top">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">AI Insight</h1>
        <p class="text-indigo-200 text-sm">Saran finansial personal</p>
      </div>
      <button on:click={generate} disabled={busy}
        class="bg-white/20 backdrop-blur-md px-4 py-2 rounded-xl text-sm font-semibold inline-flex items-center gap-1 disabled:opacity-50">
        <RefreshCcw size="16" /> {busy ? 'Generating...' : 'Generate'}
      </button>
    </div>
  </div>

  <div class="px-6 -mt-4 space-y-3">
    {#if errorMsg}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 text-sm">{errorMsg}</div>
    {/if}
    {#if loading}
      <Loader />
    {:else if insights.length === 0}
      <div class="bg-white rounded-2xl p-6 text-center border border-gray-100">
        <Sparkles class="mx-auto mb-2 text-gray-400" size="32" />
        <p class="text-sm text-gray-500">Belum ada insight. Tap <b>Generate</b>.</p>
      </div>
    {:else}
      {#each insights as i}
        <div class="bg-white rounded-2xl p-4 shadow-sm border {i.sudah_dibaca ? 'border-gray-100' : 'border-indigo-200'}">
          <div class="flex items-start justify-between gap-2">
            <div>
              <h3 class="font-bold text-indigo-900">{i.judul}</h3>
              <p class="text-sm text-gray-700 mt-1">{i.konten}</p>
              <p class="text-[10px] uppercase tracking-wider text-gray-400 mt-2">{i.tipe} · {new Date(i.created_at).toLocaleDateString('id-ID')}</p>
            </div>
            {#if !i.sudah_dibaca}
              <button on:click={() => markRead(i.id)} class="text-indigo-600"><BookmarkCheck size="20" /></button>
            {/if}
          </div>
        </div>
      {/each}
    {/if}
  </div>
</MobileShell>
