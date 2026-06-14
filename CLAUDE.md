phase 1
Setup & auth
Project init, DB, login/register
Foundation
⌄
Tasks

    Init SvelteKit + Capacitor
    Setup PostgreSQL + Alembic migration
    Seed tabel kategori (warna & icon)
    Endpoint register & login JWT
    Simpan token di Capacitor Preferences
    Halaman login & register (Svelte)
    Route guard berdasarkan token

Tech stack
SvelteKit Capacitor FastAPI PostgreSQL Alembic JWT bcrypt
Capacitor membungkus SvelteKit sebagai WebView native Android/iOS. Token disimpan di Capacitor Preferences (bukan localStorage biasa).


phase 2 frontend
svelte webview frontend and using vite
Task 
buat sesuai dengan file contoh frontend


phase 3

Transaksi manual
Input pengeluaran & pemasukan + item
Core
⌄
Tasks

    CRUD endpoint transaksi & item_transaksi
    Svelte store untuk state transaksi
    Form input manual dengan reactive binding
    Dropdown kategori dari API
    Dynamic tambah/hapus item (Svelte each block)
    Kalkulasi total otomatis via derived store
    List transaksi + infinite scroll

Tech stack
SvelteKit Svelte Store FastAPI SQLAlchemy PostgreSQL Pydantic
Gunakan writable/derived store Svelte untuk kalkulasi total real-time — tidak perlu library form eksternal.


phase 4
Scan nota (OCR + VLM)
PaddleOCR + Qwen2.5-VL ekstraksi nota
AI
⌄
Tasks

    Capacitor Camera plugin ambil foto nota
    Upload base64/blob ke FastAPI
    PaddleOCR ekstrak raw text
    Kirim gambar + text ke Qwen2.5-VL
    VLM parsing: merchant, items, harga, total
    Simpan ke tabel nota
    Auto-fill form Svelte dari hasil VLM
    User review & koreksi sebelum simpan

Tech stack
Capacitor Camera PaddleOCR Qwen2.5-VL FastAPI Pillow Transformers MinIO / S3
Capacitor Camera handle akses kamera native. Gambar dikirim sebagai base64 ke backend, semua proses AI jalan di server.


phase 5

Budget & statistik
Set budget, chart pemasukan vs pengeluaran
Analytics
⌄
Tasks

    CRUD endpoint budget per kategori/bulan
    Endpoint agregasi total & breakdown kategori
    Chart bar & pie (Svelte-kompatibel)
    Filter bulanan / mingguan / tahunan
    Indikator budget terpakai vs sisa
    Dashboard summary card (saldo, in, out)

Tech stack
SvelteKit LayerChart FastAPI PostgreSQL date-fns
LayerChart adalah charting library native Svelte. Alternatif: Chart.js via onMount atau D3 langsung di Svelte.


phase 6


AI Insight
Generate & tampilkan insight per user
AI
⌄
Tasks

    Endpoint trigger generate insight (async)
    Query agregasi transaksi user
    Kirim data ke LLM (Qwen3)
    Simpan ke tabel ai_insight
    Svelte store untuk insight state
    Insight card di dashboard & statistik
    Mark sudah_dibaca on tap

Tech stack
Qwen3 Svelte Store FastAPI PostgreSQL Celery Redis
Insight di-generate async via Celery task — UI poll atau pakai SSE (Server-Sent Events) untuk update real-time ke Svelte.

phase 7 


AI Memory
Persistensi konteks AI antar session
AI
⌄
Tasks

    Tabel ai_memory per user per topik
    Update memory setelah insight baru
    Fetch & inject memory ke system prompt
    Kompresi ringkasan memory bulanan
    Insight makin personal tiap bulan

Tech stack
Qwen3 PostgreSQL FastAPI Celery Redis
Memory di-update tiap akhir bulan via scheduled Celery beat — tidak ada perubahan di sisi Svelte/frontend.

phase 8

Polish & deploy
Profil, notifikasi, testing, production
Launch
⌄
Tasks

    Halaman profil & edit akun
    Push notifikasi via Capacitor Push
    Unit test endpoint FastAPI (pytest)
    Error handling & skeleton loading (Svelte)
    Build APK via Capacitor + Android Studio
    Docker compose (API + DB + Redis + Celery)
    Deploy backend ke VPS / Railway

Tech stack
Capacitor Push Capacitor Build Docker Nginx pytest Railway / VPS
Build APK: SvelteKit di-build jadi static, di-copy ke Capacitor Android project, lalu build via Gradle.


