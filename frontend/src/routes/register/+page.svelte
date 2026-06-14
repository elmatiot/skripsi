<script>
  import { UserPlus, Lock, Mail, User as UserIcon, Sparkles } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { register } from '$lib/auth.js';

  let nama = '';
  let email = '';
  let password = '';
  let busy = false;
  let error = '';

  async function submit() {
    error = '';
    if (password.length < 6) {
      error = 'Password minimal 6 karakter';
      return;
    }
    busy = true;
    try {
      await register(nama.trim(), email.trim(), password);
      await goto('/home');
    } catch (e) {
      error = e?.message || 'Gagal mendaftar';
    } finally {
      busy = false;
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 flex flex-col px-6 py-12 safe-top">
  <div class="flex-1 flex flex-col items-center justify-center">
    <div class="w-20 h-20 rounded-3xl bg-white/20 backdrop-blur-xl border border-white/30 flex items-center justify-center mb-6">
      <Sparkles class="text-white" size="40" />
    </div>
    <h1 class="text-white text-3xl font-bold mb-2">Buat Akun</h1>
    <p class="text-indigo-200 text-center text-sm mb-10">Mulai kelola keuangan dengan AI</p>

    <form on:submit|preventDefault={submit} class="w-full max-w-sm">
      <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
        {#if error}
          <div class="mb-4 bg-red-500/30 border border-red-300/40 text-white text-sm rounded-xl px-4 py-2">{error}</div>
        {/if}

        <div class="mb-4">
          <label class="text-white text-sm font-medium mb-2 block">Nama</label>
          <div class="relative">
            <UserIcon class="absolute left-4 top-1/2 -translate-y-1/2 text-white/60" size="20" />
            <input type="text" required bind:value={nama} placeholder="Nama lengkap"
              class="w-full pl-12 pr-4 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
          </div>
        </div>

        <div class="mb-4">
          <label class="text-white text-sm font-medium mb-2 block">Email</label>
          <div class="relative">
            <Mail class="absolute left-4 top-1/2 -translate-y-1/2 text-white/60" size="20" />
            <input type="email" required bind:value={email} placeholder="nama@email.com"
              class="w-full pl-12 pr-4 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
          </div>
        </div>

        <div class="mb-6">
          <label class="text-white text-sm font-medium mb-2 block">Password</label>
          <div class="relative">
            <Lock class="absolute left-4 top-1/2 -translate-y-1/2 text-white/60" size="20" />
            <input type="password" required bind:value={password} placeholder="Min. 6 karakter"
              class="w-full pl-12 pr-4 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
          </div>
        </div>

        <button type="submit" disabled={busy}
          class="w-full py-4 bg-white text-indigo-600 rounded-xl font-bold text-lg hover:bg-indigo-50 shadow-lg disabled:opacity-60 flex items-center justify-center gap-2">
          <UserPlus size="20" /> {busy ? 'Membuat akun...' : 'Daftar'}
        </button>

        <div class="mt-6 text-center">
          <span class="text-white/80 text-sm">Sudah punya akun? </span>
          <a href="/login" class="text-white font-semibold text-sm hover:underline">Masuk</a>
        </div>
      </div>
    </form>
  </div>
</div>
