<script>
  export let withBottomNav = true;
  import BottomNav from './BottomNav.svelte';
</script>

<div class="min-h-screen w-full bg-gray-100 flex items-center justify-center">
  <div class="relative w-full max-w-md min-h-screen bg-white shadow-2xl flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto {withBottomNav ? 'pb-24' : ''}">
      <slot />
    </div>
    {#if withBottomNav}
      <BottomNav />
    {/if}
  </div>
</div>
