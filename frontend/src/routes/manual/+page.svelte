<script>
  import { onMount } from 'svelte';
  import { ArrowLeft, Plus, Trash2 } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { derived, writable } from 'svelte/store';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import { api } from '$lib/api.js';
  import { formatRupiah } from '$lib/stores.js';

  let kategori = [];
  let tipe = 'pengeluaran';
  let kategoriId = null;
  let merchant = '';
  let deskripsi = '';
  let metodeBayar = 'tunai';
  let tanggal = new Date().toISOString().slice(0, 10);
  let nominalManual = 0;
  let busy = false;
  let error = '';
  let success = '';

  let showBuatKategori = false;
  let namaKategoriBaru = '';
  let busyKategori = false;

  const items = writable([{ nama_item: '', qty: 1, harga_satuan: 0 }]);
  const totalDerived = derived(items, ($items) =>
    $items.reduce((acc, it) => acc + Number(it.harga_satuan || 0) * Number(it.qty || 0), 0)
  );

  $: filteredKategori = kategori.filter((k) => k.tipe === tipe);

  $: if (filteredKategori.length && !filteredKategori.find((k) => k.id === kategoriId)) {
    kategoriId = filteredKategori[0]?.id ?? null;
  }

  onMount(async () => {
    kategori = await api.listKategori();
  });

  async function simpanKategoriBaru() {
    if (!namaKategoriBaru.trim()) return;
    busyKategori = true;
    try {
      const baru = await api.createKategori({ nama: namaKategoriBaru.trim(), tipe });
      if (!kategori.find((k) => k.id === baru.id)) kategori = [...kategori, baru];
      kategoriId = baru.id;
      namaKategoriBaru = '';
      showBuatKategori = false;
    } catch (e) {
      error = e?.message || 'Gagal membuat kategori';
    } finally {
      busyKategori = false;
    }
  }

  function addItem() {
    items.update((arr) => [...arr, { nama_item: '', qty: 1, harga_satuan: 0 }]);
  }
  function removeItem(idx) {
    items.update((arr) => arr.filter((_, i) => i !== idx));
  }

  async function submit() {
    error = '';
    success = '';
    if (!kategoriId) return (error = 'Kategori wajib dipilih');

    const validItems = $items
      .filter((i) => i.nama_item.trim() && Number(i.harga_satuan) > 0)
      .map((i) => ({
        nama_item: i.nama_item.trim(),
        qty: Number(i.qty),
        harga_satuan: Number(i.harga_satuan)
      }));

    const nominalFinal = validItems.length ? $totalDerived : Number(nominalManual) || 0;
    if (nominalFinal <= 0) return (error = 'Nominal harus > 0');

    const payload = {
      kategori_id: kategoriId,
      nominal: nominalFinal,
      merchant: merchant.trim() || null,
      tanggal_transaksi: tanggal,
      deskripsi: deskripsi.trim() || null,
      metode_bayar: metodeBayar || null,
      items: validItems
    };

    busy = true;
    try {
      await api.createTransaksi(payload);
      success = 'Tersimpan!';
      setTimeout(() => goto('/home'), 600);
    } catch (e) {
      error = e?.message || 'Gagal menyimpan';
    } finally {
      busy = false;
    }
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-b from-indigo-600 to-purple-600 text-white px-6 pt-12 pb-6 safe-top">
    <button on:click={() => goto('/home')} class="mb-4 inline-flex items-center gap-1 text-white/80">
      <ArrowLeft size="20" /> Kembali
    </button>
    <h1 class="text-2xl font-bold">Catat Transaksi</h1>
    <p class="text-indigo-200 text-sm">Input pemasukan / pengeluaran manual</p>
  </div>

  <div class="px-6 -mt-4">
    <div class="bg-white rounded-2xl p-5 shadow-sm space-y-4 border border-gray-100">
      <div class="grid grid-cols-2 gap-2">
        <button class="py-3 rounded-xl font-semibold {tipe === 'pengeluaran' ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600'}"
          on:click={() => (tipe = 'pengeluaran')}>Pengeluaran</button>
        <button class="py-3 rounded-xl font-semibold {tipe === 'pemasukan' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600'}"
          on:click={() => (tipe = 'pemasukan')}>Pemasukan</button>
      </div>

      {#if error}<p class="text-sm text-red-600">{error}</p>{/if}
      {#if success}<p class="text-sm text-green-600">{success}</p>{/if}

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block">Merchant / Sumber</label>
        <input type="text" bind:value={merchant} placeholder="Contoh: Indomaret / Gaji bulanan"
          class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-indigo-500" />
      </div>

      <div>
        <div class="flex items-center justify-between mb-1">
          <label class="text-sm font-medium text-gray-700">Kategori</label>
          <button type="button" on:click={() => { showBuatKategori = !showBuatKategori; namaKategoriBaru = ''; }}
            class="text-xs text-indigo-600 font-medium">
            {showBuatKategori ? 'Batal' : '+ Buat baru'}
          </button>
        </div>
        {#if showBuatKategori}
          <div class="flex gap-2 mb-2">
            <input type="text" bind:value={namaKategoriBaru} placeholder="Nama kategori baru"
              class="flex-1 px-3 py-2 border border-indigo-300 rounded-xl text-sm focus:outline-none focus:border-indigo-500" />
            <button type="button" on:click={simpanKategoriBaru} disabled={busyKategori || !namaKategoriBaru.trim()}
              class="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold disabled:opacity-50">
              {busyKategori ? '...' : 'Simpan'}
            </button>
          </div>
        {/if}
        <select bind:value={kategoriId} class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white">
          {#if filteredKategori.length === 0}
            <option disabled value={null}>Belum ada kategori — buat baru di atas</option>
          {/if}
          {#each filteredKategori as k}
            <option value={k.id}>{k.nama}</option>
          {/each}
        </select>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block">Tanggal</label>
          <input type="date" bind:value={tanggal} class="w-full px-4 py-3 border border-gray-200 rounded-xl" />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block">Metode Bayar</label>
          <select bind:value={metodeBayar} class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white">
            <option value="tunai">Tunai</option>
            <option value="transfer">Transfer</option>
            <option value="qris">QRIS</option>
            <option value="kartu">Kartu</option>
            <option value="ewallet">E-Wallet</option>
          </select>
        </div>
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block">Deskripsi (opsional)</label>
        <textarea bind:value={deskripsi} rows="2"
          class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-indigo-500"></textarea>
      </div>

      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium text-gray-700">Item (opsional, otomatis menjadi nominal)</label>
          <button on:click={addItem} class="text-xs font-medium text-indigo-600 inline-flex items-center gap-1">
            <Plus size="14" /> Tambah
          </button>
        </div>
        <div class="space-y-2">
          {#each $items as it, idx}
            <div class="bg-gray-50 rounded-xl p-3 grid grid-cols-12 gap-2 items-center">
              <input type="text" placeholder="Nama item" bind:value={it.nama_item}
                class="col-span-5 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <input type="number" min="1" bind:value={it.qty}
                class="col-span-2 px-3 py-2 border border-gray-200 rounded-lg text-sm text-center" />
              <input type="number" min="0" bind:value={it.harga_satuan} placeholder="Harga"
                class="col-span-4 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <button on:click={() => removeItem(idx)} class="col-span-1 text-red-500"><Trash2 size="16" /></button>
            </div>
          {/each}
        </div>
        <p class="text-right text-sm text-gray-600 mt-2">
          Subtotal item: <span class="font-bold text-indigo-600">{formatRupiah($totalDerived)}</span>
        </p>
      </div>

      {#if $totalDerived === 0}
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block">Nominal manual</label>
          <input type="number" min="0" bind:value={nominalManual} placeholder="0"
            class="w-full px-4 py-3 border border-gray-200 rounded-xl" />
        </div>
      {/if}

      <button on:click={submit} disabled={busy}
        class="w-full py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold disabled:opacity-60">
        {busy ? 'Menyimpan...' : 'Simpan Transaksi'}
      </button>
    </div>
  </div>
</MobileShell>
