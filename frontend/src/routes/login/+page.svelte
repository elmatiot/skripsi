<script>
  import { Eye, EyeOff, Lock, Mail, Sparkles } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { login } from '$lib/auth.js';

  let email = '';
  let password = '';
  let showPassword = false;
  let busy = false;
  let error = '';

  async function submit() {
    error = '';
    busy = true;
    try {
      await login(email.trim(), password);
      await goto('/home');
    } catch (e) {
      error = e?.message || 'Gagal masuk';
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
    <h1 class="text-white text-3xl font-bold mb-2">FinanceAI</h1>
    <p class="text-indigo-200 text-center text-sm mb-12">Kelola keuangan Anda dengan cerdas</p>

    <form on:submit|preventDefault={submit} class="w-full max-w-sm">
      <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
        <h2 class="text-white text-2xl font-bold mb-6 text-center">Masuk</h2>

        {#if error}
          <div class="mb-4 bg-red-500/30 border border-red-300/40 text-white text-sm rounded-xl px-4 py-2">
            {error}
          </div>
        {/if}

        <div class="mb-4">
          <label class="text-white text-sm font-medium mb-2 block">Email</label>
          <div class="relative">
            <Mail class="absolute left-4 top-1/2 -translate-y-1/2 text-white/60" size="20" />
            <input
              type="email" required bind:value={email}
              placeholder="nama@email.com"
              class="w-full pl-12 pr-4 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
          </div>
        </div>

        <div class="mb-6">
          <label class="text-white text-sm font-medium mb-2 block">Password</label>
          <div class="relative">
            <Lock class="absolute left-4 top-1/2 -translate-y-1/2 text-white/60" size="20" />
            {#if showPassword}
              <input type="text" required bind:value={password}
                placeholder="Masukkan password"
                class="w-full pl-12 pr-12 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
            {:else}
              <input type="password" required bind:value={password}
                placeholder="Masukkan password"
                class="w-full pl-12 pr-12 py-3.5 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:border-white/50" />
            {/if}
            <button type="button" on:click={() => (showPassword = !showPassword)}
              class="absolute right-4 top-1/2 -translate-y-1/2 text-white/60">
              {#if showPassword}<EyeOff size="20" />{:else}<Eye size="20" />{/if}
            </button>
          </div>
        </div>

        <button type="submit" disabled={busy}
          class="w-full py-4 bg-white text-indigo-600 rounded-xl font-bold text-lg hover:bg-indigo-50 shadow-lg disabled:opacity-60">
          {busy ? 'Memproses...' : 'Masuk'}
        </button>

        <div class="mt-6 text-center">
          <span class="text-white/80 text-sm">Belum punya akun? </span>
          <a href="/register" class="text-white font-semibold text-sm hover:underline">Daftar sekarang</a>
        </div>
      </div>
    </form>
  </div>

  <div class="text-center text-white/60 text-xs mt-8">© 2026 FinanceAI</div>
</div>
