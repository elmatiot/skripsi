<script>
  import { onMount } from 'svelte';
  import { LogOut, Save, BrainCircuit, Bell } from 'lucide-svelte';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import { api } from '$lib/api.js';
  import { user } from '$lib/stores.js';
  import { logout } from '$lib/auth.js';

  let nama = '';
  let busy = false;
  let msg = '';

  onMount(async () => {
    const me = await api.getProfile();
    user.set(me);
    nama = me.nama || '';
  });

  async function save() {
    busy = true;
    msg = '';
    try {
      const me = await api.updateProfile({ nama });
      user.set(me);
      msg = 'Profil disimpan!';
    } catch (e) {
      msg = e?.message || 'Gagal menyimpan';
    } finally {
      busy = false;
    }
  }

  async function enablePush() {
    try {
      const { PushNotifications } = await import('@capacitor/push-notifications');
      const perm = await PushNotifications.requestPermissions();
      if (perm.receive === 'granted') {
        await PushNotifications.register();
        msg = 'Notifikasi diaktifkan';
      } else {
        msg = 'Izin ditolak';
      }
    } catch {
      msg = 'Push notifikasi hanya jalan di build native (Capacitor)';
    }
  }

  async function triggerCompress() {
    try {
      await api.triggerCompressMemory();
      msg = 'Kompresi memory dijadwalkan';
    } catch (e) {
      msg = e?.message || 'Gagal';
    }
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-indigo-600 to-purple-700 text-white px-6 pt-12 pb-10 safe-top text-center">
    <div class="w-20 h-20 rounded-full bg-white/20 mx-auto flex items-center justify-center text-2xl font-bold">
      {($user?.nama || 'U').slice(0, 1).toUpperCase()}
    </div>
    <h1 class="mt-3 text-2xl font-bold">{$user?.nama}</h1>
    <p class="text-indigo-200 text-sm">{$user?.email}</p>
  </div>

  <div class="px-6 -mt-4 space-y-4">
    {#if msg}<p class="bg-white border border-gray-100 rounded-xl px-4 py-2 text-sm text-gray-700">{msg}</p>{/if}

    <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 space-y-3">
      <h3 class="font-bold text-gray-800">Edit Profil</h3>
      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block">Nama</label>
        <input bind:value={nama} class="w-full px-3 py-2 border rounded-lg" />
      </div>
      <button on:click={save} disabled={busy}
        class="w-full py-3 rounded-xl bg-indigo-600 text-white font-bold inline-flex items-center justify-center gap-2 disabled:opacity-60">
        <Save size="18" /> {busy ? 'Menyimpan...' : 'Simpan'}
      </button>
    </div>

    <div class="bg-white rounded-2xl divide-y border border-gray-100">
      <button on:click={enablePush} class="w-full px-4 py-4 flex items-center justify-between">
        <span class="inline-flex items-center gap-3 text-gray-700"><Bell size="18" /> Aktifkan Notifikasi</span>
        <span class="text-xs text-gray-400">Capacitor Push</span>
      </button>
      <button on:click={triggerCompress} class="w-full px-4 py-4 flex items-center justify-between">
        <span class="inline-flex items-center gap-3 text-gray-700"><BrainCircuit size="18" /> Kompres Memory AI</span>
        <span class="text-xs text-gray-400">Async</span>
      </button>
      <a href="/insight" class="w-full px-4 py-4 flex items-center justify-between">
        <span class="text-gray-700">AI Insight</span>
        <span class="text-xs text-gray-400">›</span>
      </a>
    </div>

    <button on:click={logout}
      class="w-full py-3 rounded-xl bg-red-50 text-red-600 font-bold border border-red-100 inline-flex items-center justify-center gap-2">
      <LogOut size="18" /> Keluar
    </button>
  </div>
</MobileShell>
