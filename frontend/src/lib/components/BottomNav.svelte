<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Home, Wallet, ScanLine, BarChart3, User } from 'lucide-svelte';

  $: path = $page.url.pathname;
  $: isActive = (p) => path === p || (p !== '/' && path.startsWith(p));
</script>

<nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-200 px-6 py-3 safe-bottom z-30">
  <div class="flex items-center justify-around">
    <button class="flex flex-col items-center gap-1 py-2 px-3 transition-colors {isActive('/home') ? 'text-indigo-600' : 'text-gray-400'}" on:click={() => goto('/home')}>
      <Home size="24" strokeWidth={isActive('/home') ? 2.5 : 2} />
      <span class="text-xs font-medium">Home</span>
    </button>

    <button class="flex flex-col items-center gap-1 py-2 px-3 transition-colors {isActive('/budget') ? 'text-indigo-600' : 'text-gray-400'}" on:click={() => goto('/budget')}>
      <Wallet size="24" strokeWidth={isActive('/budget') ? 2.5 : 2} />
      <span class="text-xs font-medium">Budget</span>
    </button>

    <button class="relative -mt-6" on:click={() => goto('/scan')}>
      <div class="w-16 h-16 rounded-full flex items-center justify-center shadow-lg {isActive('/scan') ? 'bg-indigo-600' : 'bg-gradient-to-br from-indigo-600 to-purple-600'}">
        <ScanLine class="text-white" size="28" strokeWidth="2.5" />
      </div>
      <span class="absolute -bottom-5 left-1/2 -translate-x-1/2 text-xs font-medium whitespace-nowrap {isActive('/scan') ? 'text-indigo-600' : 'text-gray-400'}">Scan</span>
    </button>

    <button class="flex flex-col items-center gap-1 py-2 px-3 transition-colors {isActive('/statistik') ? 'text-indigo-600' : 'text-gray-400'}" on:click={() => goto('/statistik')}>
      <BarChart3 size="24" strokeWidth={isActive('/statistik') ? 2.5 : 2} />
      <span class="text-xs font-medium">Statistik</span>
    </button>

    <button class="flex flex-col items-center gap-1 py-2 px-3 transition-colors {isActive('/profil') ? 'text-indigo-600' : 'text-gray-400'}" on:click={() => goto('/profil')}>
      <User size="24" strokeWidth={isActive('/profil') ? 2.5 : 2} />
      <span class="text-xs font-medium">Profil</span>
    </button>
  </div>
</nav>
