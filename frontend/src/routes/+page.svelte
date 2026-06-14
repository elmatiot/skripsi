<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { isAuthed } from '$lib/stores.js';

  onMount(() => {
    goto(get(isAuthed) ? '/home' : '/login');
  });
</script>
