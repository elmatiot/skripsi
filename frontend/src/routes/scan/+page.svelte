<script>
  import { onMount } from 'svelte';
  import { ArrowLeft, Camera, Upload, Loader2, AlertTriangle } from 'lucide-svelte';
  import { goto } from '$app/navigation';

  import MobileShell from '$lib/components/MobileShell.svelte';
  import { api } from '$lib/api.js';
  import { formatRupiah } from '$lib/stores.js';

  let file = null;
  let preview = '';
  let busy = false;
  let result = null;
  let error = '';
  let kategoriList = [];

  onMount(async () => {
    kategoriList = await api.listKategori('pengeluaran');
  });

  function onPick(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    file = f;
    preview = URL.createObjectURL(f);
    result = null;
    error = '';
  }

  async function takePhotoNative() {
    try {
      const { Camera, CameraResultType, CameraSource } = await import('@capacitor/camera');
      const photo = await Camera.getPhoto({
        quality: 80,
        resultType: CameraResultType.DataUrl,
        source: CameraSource.Camera,
        allowEditing: false
      });
      const res = await fetch(photo.dataUrl);
      file = new File([await res.blob()], 'nota.jpg', { type: 'image/jpeg' });
      preview = photo.dataUrl;
      result = null;
      error = '';
    } catch {
      document.getElementById('file-input')?.click();
    }
  }

  async function analyze() {
    if (!file) return (error = 'Pilih atau ambil foto nota dulu');
    busy = true;
    error = '';
    result = null;
    try {
      result = await api.analyzeNota(file);
    } catch (e) {
      error = e?.message || 'Gagal menganalisa nota';
    } finally {
      busy = false;
    }
  }

  async function saveTransaksi() {
    if (!result || result.ocr_status !== 'Sesuai') return;
    let kat = kategoriList.find(
      (k) => k.nama?.toLowerCase() === (result.kategori || '').toLowerCase()
    );
    if (!kat && result.kategori) {
      kat = await api.createKategori({ nama: result.kategori, tipe: 'pengeluaran' });
      kategoriList = [...kategoriList, kat];
    }
    if (!kat) kat = kategoriList[0];
    if (!kat) return (error = 'Pilih atau buat kategori dulu');
    const payload = {
      kategori_id: kat.id,
      nominal: Number(result.total) || 0,
      merchant: result.merchant || null,
      tanggal_transaksi: new Date().toISOString().slice(0, 10),
      deskripsi: null,
      metode_bayar: null,
      nota_id: result.nota_id,
      items: (result.items || []).map((it) => ({
        nama_item: it.nama_item || it.nama || '',
        qty: Number(it.qty || it.jumlah) || 1,
        harga_satuan: Number(it.harga_satuan || it.harga) || 0
      }))
    };
    await api.createTransaksi(payload);
    await goto('/home');
  }
</script>

<MobileShell>
  <div class="bg-gradient-to-br from-purple-600 to-indigo-700 text-white px-6 pt-12 pb-8 safe-top">
    <button on:click={() => goto('/home')} class="mb-4 inline-flex items-center gap-1 text-white/80">
      <ArrowLeft size="20" /> Kembali
    </button>
    <h1 class="text-2xl font-bold">Scan Nota</h1>
    <p class="text-indigo-200 text-sm">PaddleOCR + DeepSeek</p>
  </div>

  <div class="px-6 -mt-4 space-y-4">
    <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-3">
      <input id="file-input" type="file" accept="image/*" capture="environment" on:change={onPick} class="hidden" />
      <div class="grid grid-cols-2 gap-2">
        <button on:click={takePhotoNative} class="bg-indigo-600 text-white py-3 rounded-xl font-semibold inline-flex items-center justify-center gap-2">
          <Camera size="18" /> Ambil Foto
        </button>
        <label for="file-input" class="bg-gray-100 text-gray-700 py-3 rounded-xl font-semibold inline-flex items-center justify-center gap-2 cursor-pointer">
          <Upload size="18" /> Pilih File
        </label>
      </div>

      {#if preview}
        <img src={preview} alt="nota" class="w-full rounded-xl border" />
      {/if}

      <button on:click={analyze} disabled={!file || busy}
        class="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold disabled:opacity-60 inline-flex items-center justify-center gap-2">
        {#if busy}<Loader2 class="animate-spin" size="18" /> Menganalisa...{:else}Analisa Nota{/if}
      </button>
      {#if error}<p class="text-sm text-red-600">{error}</p>{/if}
    </div>

    {#if result}
      <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-3">
        {#if result.ocr_status !== 'Sesuai'}
          <div class="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 inline-flex items-center gap-2">
            <AlertTriangle size="18" />
            <span class="text-sm">OCR tidak sesuai. Coba foto nota yang lebih jelas.</span>
          </div>
        {:else}
          <h3 class="font-bold text-gray-800">{result.merchant || 'Tanpa Merchant'}</h3>
          <p class="text-xs text-gray-500">Kategori: {result.kategori || '-'}</p>
          <ul class="text-sm divide-y border rounded-xl">
            {#each result.items as it}
              <li class="px-3 py-2 flex justify-between">
                <span>{it.nama_item} × {it.qty}</span>
                <span class="font-medium">{formatRupiah(Number(it.harga_satuan) * Number(it.qty))}</span>
              </li>
            {/each}
          </ul>
          <p class="text-right font-bold text-indigo-700">Total: {formatRupiah(result.total)}</p>
          <button on:click={saveTransaksi}
            class="w-full py-3 rounded-xl bg-green-500 text-white font-bold">Simpan ke Transaksi</button>
        {/if}
      </div>
    {/if}
  </div>
</MobileShell>
