<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  import { hydrateAuth } from '$lib/auth.js';
  import { isAuthed } from '$lib/stores.js';

  let booting = true;

  const PUBLIC_PATHS = ['/login', '/register'];

  onMount(async () => {
    await hydrateAuth();
    booting = false;

    isAuthed.subscribe((auth) => {
      const path = $page.url.pathname;
      const isPublic = PUBLIC_PATHS.some((p) => path === p || path.startsWith(p + '/'));
      if (!auth && !isPublic) goto('/login');
      if (auth && (path === '/' || isPublic)) goto('/home');
    });
  });
</script>

{#if booting}
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-600">
    <div class="text-white text-sm flex items-center gap-3">
      <div class="w-6 h-6 border-2 border-white/40 border-t-white rounded-full animate-spin"></div>
      Memuat...
    </div>
  </div>
{:else}
  <slot />
{/if}
