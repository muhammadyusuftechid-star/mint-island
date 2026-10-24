# 🗺️ ROADMAP & TAHAPAN PENGEMBANGAN MINT-ISLAND

Dokumen ini memetakan tahapan pengembangan aplikasi secara bertahap dan terukur.

---

## 📊 Status Ringkasan Proyek

| Fase | Nama Tahapan | Status | Hasil Akhir |
| :---: | :--- | :---: | :--- |
| **0** | **Riset, Desain, & Governance** | ✅ **SELESAI** | Rancangan, AGENTS.md, Rules, Changelog |
| **1** | **Pondasi Window Kapsul & Autostart** | ✅ **SELESAI** | Jendela melayang X11 & autostart reboot |
| **2** | **Hardware Event Listeners (HUD)** | ✅ **SELESAI** | Volume, kecerahan, & animasi charger |
| **3** | **YouTube Player & Lirik Karaoke** | ✅ **SELESAI** | Deteksi lagu YouTube & lirik real-time |
| **4** | **Menu Pengaturan & System Tray** | ✅ **SELESAI** | Control Panel GUI & ikon baki Linux Mint |
| **5** | **Optimasi, Uji Reboot, & Installer** | ✅ **SELESAI** | Konsumsi <45MB RAM & skrip instalasi |
| **S1-S4** | **Komersial: MoR, Toko, & Packaging** | ✅ **SELESAI** | Paket .deb, landing page web, mesin lisensi |
| **S5** | **Senior Dev Clean Code Overhaul** | ✅ **SELESAI** | Anti-AI slop, memory hygiene, X11 caching |
| **S6** | **Persistent Control Center & Full Audit** | ✅ **SELESAI** | Baterai/Volume persisten, eliminasi HUD collision, bebas lisensi |
| **S7** | **Power Profile Switcher & Battery Health** | ✅ **SELESAI** | Pengalih 3 mode daya (Power Saver/Balanced/Perf) & estimasi baterai |
| **S8** | **Desktop Notification HUD Pill** | ✅ **SELESAI** | Kapsul mekar menangkap notifikasi pesan, download, email, terminal |
| **S9** | **Bluetooth & TWS Headphone HUD** | ✅ **SELESAI** | Popup otomatis nama & baterai saat TWS/headphone terhubung |
| **S10** | **Compact Micro-Pill & Hover/Song Peek** | ✅ **SELESAI** | Kapsul ramping ~120px saat normal, mekar saat hover/ganti lagu |
| **S11** | **Backend Audit & Robustness Hardening** | ✅ **SELESAI** | Audit 8 modul D-Bus, RAM cache capping, Unicode dashes, & UPower threshold |
| **S12** | **Clean Code & Industry Standard Overhaul** | ✅ **SELESAI** | pyproject.toml PEP 621, test suite unittest, eliminasi magic numbers, & OOP encapsulation |
| **v1.0.0** | **Inaugural Public Release** | 🚀 **PUBLISHED** | Repositori publik GitHub, rilis tag v1.0.0, dokumentasi lengkap |

---

## 🛠️ Rincian Pekerjaan Tiap Fase

### ✅ Fase 0: Riset, Arsitektur, & Standar Proyek (Selesai)
- [x] Analisis kesiapan sistem Linux Mint 22.3 Cinnamon X11.
- [x] Pembuatan [RANCANGAN_DYNAMIC_ISLAND_LINUX_MINT.md](file:///home/yusuf/projekan/lapatop%20app/RANCANGAN_DYNAMIC_ISLAND_LINUX_MINT.md).
- [x] Pembuatan aturan tata kelola di [.agents/rules/](file:///home/yusuf/projekan/lapatop%20app/.agents/rules/).
- [x] Pembuatan master intruksi [AGENTS.md](file:///home/yusuf/projekan/lapatop%20app/AGENTS.md).
- [x] Pembuatan [CHANGELOG.md](file:///home/yusuf/projekan/lapatop%20app/CHANGELOG.md).

---

### ✅ Fase 1: Pondasi Window Kapsul & Autostart (Selesai)
- [x] **Modul Konfigurasi (`config.py`):**
  - Membuat dan membaca `~/.config/dynamic-island/config.json`.
- [x] **Modul Autostart (`autostart.py`):**
  - Memasang/mencabut file `~/.config/autostart/mint-island.desktop`.
- [x] **Jendela Utama GTK4 (`ui/island_window.py`):**
  - Jendela transparan di bagian atas tengah layar (*top-center*).
  - Window hints: `keep_above`, `skip_taskbar`, `skip_pager`, `set_decorated(False)`, `_NET_WM_WINDOW_TYPE_DOCK`.
  - Desain CSS kapsul (*pill shape*) modern dengan warna gelap dan border tipis.
- [x] **Pengujian Fase 1:** Jendela kapsul muncul di layar, interactive click card, dan bertahan saat membuka aplikasi lain.

---

### ✅ Fase 2: Hardware Event Listeners (Volume, Kecerahan, Baterai HUD) (Selesai)
- [x] **Battery Listener (`modules/battery_module.py`):**
  - Membaca sinyal UPower D-Bus (charger dicolok/dicabut, persentase baterai, peringatan baterai lemah).
- [x] **Volume Listener (`modules/volume_module.py`):**
  - Membaca sinyal audio PipeWire / `pactl` secara real-time via background subscriber thread.
- [x] **Brightness Listener (`modules/brightness_module.py`):**
  - Membaca sinyal perubahan `org.cinnamon.SettingsDaemon.Power.Screen` dan fallback sysfs.
- [x] **Animasi HUD Mekar:**
  - Animasi pulau memanjang (lebar 270px) menampilkan ikon + progress bar + persentase selama 3 detik, lalu menciut kembali ke ukuran kapsul mini secara halus.
- [x] **Pengujian Fase 2:** Event volume pactl dan signal UPower teruji berjalan tanpa blocking UI thread.

---

### ✅ Fase 3: Pemutar YouTube & Mesin Lirik Karaoke Real-Time (Selesai)
- [x] **MPRIS Media Listener (`modules/mpris_module.py`):**
  - Menangkap lagu yang diputar di YouTube (Brave/Chrome/Firefox), Spotify, VLC.
  - Mengambil judul lagu, nama artis, seekbar position, durasi, dan kontrol Play/Pause/Next/Prev.
- [x] **Mesin Lirik Synced (`modules/lyrics_module.py`):**
  - Pembersih judul otomatis (menghapus teks *"Official Video"*, *"[4K]"*, dll).
  - Mengambil lirik dari LRCLIB API secara asinkron di background thread.
  - Sinkronisasi detik musik dengan baris lirik (karaoke timing).
- [x] **Tampilan Lirik & Media:**
  - Satu baris lirik subtitle di kapsul atas saat lagu diputar.
  - Kartu kontrol musik penuh saat diklik dengan seekbar progres dan 3-baris karaoke lirik aktif menyala hijau mint.
- [x] **Pengujian Fase 3:** Teruji langsung membaca MPRIS Brave dan sinkronisasi LRCLIB.

---

### ✅ Fase 4: Menu Pengaturan (Control Panel GUI) & System Tray (Selesai)
- [x] **System Tray (`ui/tray_indicator.py`):**
  - Ikon di pojok kanan bawah panel Linux Mint Cinnamon (StatusNotifierItem).
  - Klik kiri/kanan membuka Control Panel Pengaturan, klik tengah untuk toggle pulau.
- [x] **Control Panel Window (`ui/settings_window.py`):**
  - Jendela pengaturan modern Libadwaita (`Adw.PreferencesWindow`).
  - Saklar utama ON/OFF, Autostart switch, Switch tiap modul (Baterai, Volume, Kecerahan, Lirik, Media).
  - Slider Margin Y (offset vertikal) dan durasi HUD dengan respon live update instan.
- [x] **Pengujian Fase 4:** Ubah opsi di jendela pengaturan -> perubahan langsung diterapkan seketika ke Dynamic Island tanpa restart.

---

### ✅ Fase 5: Optimasi Ringan, Uji Reboot, & Installer (Selesai)
- [x] **Optimasi Resource:**
  - Profiling memori diverifikasi (~45 MB private RSS, aman sesuai constraint).
  - Profiling CPU diverifikasi (0.0% CPU saat idle tanpa rendering berulang).
- [x] **Uji Persistensi Reboot:**
  - File desktop terpasang di `~/.config/autostart/mint-island.desktop` dan teruji auto-start.
- [x] **Pintasan Menu Aplikasi & Ikon:**
  - Ikon vektor SVG modern di `~/.local/share/icons/hicolor/scalable/apps/mint-island.svg`.
  - Pintasan desktop terpasang di `~/.local/share/applications/mint-island.desktop` dan `mint-island-settings.desktop`.
- [x] **Skrip Installer & Uninstaller:**
  - `install.sh`: Instalasi satu perintah langsung aktif.
  - `uninstall.sh`: Pencopotan bersih tanpa residu.

---

## 🚀 Peta Jalan Rilis Komersial (Commercial Release Roadmaps)

### ✅ Sprint 1: Portabilitas & Multi-Monitor Universal (Selesai)
- [x] **Standarisasi Path Dinamis & XDG:**
  - Menghapus semua hardcoded paths, migrasi konfigurasi ke `~/.config/mint-island/config.json`.
  - Cache lirik offline persisten di `~/.cache/mint-island/lyrics/`.
- [x] **Dukungan Multi-Monitor Dinamis:**
  - Deteksi otomatis monitor via GDK Display (`get_monitors()`).
  - Pemilihan monitor via `Adw.ComboRow` di Control Panel Pengaturan dengan live update seketika.
  - Reposisi X11 cerdas berbasis koordinat monitor target via `wmctrl`.
  - Listener perubahan monitor (`items-changed`) untuk hot-plugging layar.
- [x] **Resiliensi Jaringan & Offline Lyrics:**
  - Fallback aman dengan timeout 4-5 detik jika offline / jaringan lambat.
  - Pembacaan instan dari cache disk lokal tanpa lag saat memainkan lagu yang pernah didengarkan.

### ✅ Sprint 2: Packaging Biner Standar Komersial (.deb & ELF) (Selesai)
- [x] **Kompilasi Mesin Biner Native via Nuitka (`scripts/build_binary.sh`):**
  - Menerjemahkan kode Python ke bahasa C dan mengompilasinya menjadi file executable ELF 64-bit (`build/nuitka/mint-island-bin`, 13 MB).
  - Melindungi kekayaan intelektual (source code tidak dapat dibaca, anti-reverse engineering).
- [x] **Skrip Generator Paket Debian (`scripts/build_deb.sh`):**
  - Menghasilkan dua varian paket siap rilis di `dist/`:
    1. `mint-island_1.1.0_all.deb` (54 KB): Format ringan standar Debian/Ubuntu dengan modul Python terkompilasi bytecode `.pyc`.
    2. `mint-island_1.1.0_amd64.deb` (3.3 MB): Format komersial proteksi biner mesin ELF mandiri.
  - Lengkap dengan struktur standar: `DEBIAN/control`, `postinst`, `prerm`, `postrm`, menu `.desktop`, ikon HD, dan dokumentasi hak cipta.
- [x] **Pengujian Ekstraksi & Eksekusi Paket:**
  - Teruji mandiri diekstrak dan dijalankan dengan status `exit code 0` tanpa dependensi source code mentah.

### ✅ Sprint 3: Sistem Lisensi Digital & Multi-Bahasa (Selesai)
- [x] **Tab Aktivasi Lisensi di Control Panel (`ui/settings_window.py`):**
  - Antarmuka tab ganda modern Libadwaita (`Preferences` & `License`).
  - Baris input kunci lisensi dengan apply button otomatis (`Adw.EntryRow`), status badge, tombol aktivasi/deaktivasi, dan tautan belanja resmi.
- [x] **Mesin Lisensi & Hak Cipta Komersial (`mint_island/license.py`):**
  - Dukungan validasi online ke API Lemon Squeezy dan Gumroad.
  - Dukungan validasi format kunci kriptografi offline (`ISL-PRO-...`).
  - Penyimpanan token terenkripsi HMAC-SHA256 yang terikat pada ID perangkat keras laptop (`/etc/machine-id`).
- [x] **Sistem Internasionalisasi & Multi-Bahasa (`mint_island/i18n.py`):**
  - Dukungan dwibahasa: Bahasa Indonesia & English (US).
  - Pilihan bahasa dinamis di menu pengaturan dengan deteksi otomatis sistem operasi.
  - Standarisasi Pango markup aman bebas peringatan entitas.

### ✅ Sprint 4: Toko Online, Landing Page, & Peluncuran Komunitas (Selesai)
- [x] **Landing Page Komersial Interaktif (`web/`):**
  - Situs web modern berbasis Vanilla HTML5/CSS3/ES6 dengan tema dark glassmorphism dan token desain premium.
  - Simulator Dynamic Island interaktif (`web/app.js`) dengan tombol pemicu langsung (Idle Capsule, Volume HUD, Brightness, Charger, dan Music).
  - Engine sinkronisasi lirik karaoke real-time per detik (Queen - Bohemian Rhapsody) dengan animasi progress bar dan pemutar musik.
  - Validator uji coba kunci lisensi interaktif dengan simulasi verifikasi tanda tangan perangkat keras HMAC (`ISL-DEV-PROTEST-2026`).
  - Modal checkout instan langsung terintegrasi simulator kunci lisensi dan instruksi aktivasi.
  - Widget terminal instalasi cepat satu-klik copy clipboard (`curl ... | bash`).
  - Tabel perbandingan tolok ukur (RAM <45MB vs Electron 300MB+, CPU 0.0%).
- [x] **Panduan Setup Toko Online Komersial ([PANDUAN_SETUP_TOKO_ONLINE.md](file:///home/yusuf/projekan/lapatop%20app/PANDUAN_SETUP_TOKO_ONLINE.md)):**
  - Panduan lengkap Merchant of Record (MoR) Lemon Squeezy & Gumroad untuk kreator Indonesia.
  - Konfigurasi produk digital, aktivasi kunci lisensi unik (limit 3 PC), dan skema harga ($8 / Rp 120.000).
  - Panduan pencairan payout ke rekening bank Indonesia (BCA/Mandiri/BRI) via Wise USD atau PayPal.
  - Template email konfirmasi pembelian otomatis dan SOP garansi 14 hari uang kembali.
- [x] **Materi Pemasaran & Peluncuran Komunitas ([KOMUNITAS_DAN_PROMOSI.md](file:///home/yusuf/projekan/lapatop%20app/KOMUNITAS_DAN_PROMOSI.md)):**
  - Copywriting peluncuran untuk Reddit (`r/linuxmint`, `r/unixporn`, `r/linux`).
  - Naskah tweet dan postingan video untuk Twitter/X dan Bluesky.
  - Naskah postingan komunitas Linux Indonesia (Facebook Linux Mint Indonesia, KPLI, Telegram).
  - SOP respon FAQ dan penanganan sanggahan teknis/lisensi komunitas.

---

### ✅ Sprint 5: Senior Dev Clean Code Architecture & Anti-AI Slop (Selesai)
- [x] **Pembersihan Magic Numbers & Arsitektur Geometri (`IslandDimensions`):**
  - Semua konstanta lebar dan tinggi jendela diisolasi dalam satu namespace terpusat.
  - Eliminasi bug event bubbling: Gestur klik dipisahkan secara eksklusif ke kapsul, mencegah kartu media tertutup saat pengguna mengklik seekbar, tombol play/pause, atau teks lirik.
  - Tombol tutup kartu eksplisit (✕) ditambahkan ke header media.
- [x] **Optimasi Kinerja X11 & Subprocess Caching:**
  - Penambahan cache `_last_geometry` pada `reposition()` guna mencegah pemanggilan berulang `wmctrl` via subprocess jika posisi jendela tidak berubah.
- [x] **Higienitas Memori RAM & Throttling Jaringan:**
  - Pemanggilan `lyrics_engine.clear()` saat media berhenti untuk mengosongkan memori lirik (mempertahankan aturan RAM <45MB).
  - Deduplikasi request *in-flight* dan perlindungan throttling 30 detik untuk kegagalan LRCLIB (mencegah freezing dan network hammering).
- [x] **Perbaikan Hierarki Window & CSS Libadwaita:**
  - Isolasi CSS background transparan secara ketat ke `window.island-window`.
  - Jendela pengaturan (`window.settings-window`) menggunakan background gelap solid 100% opak (`#242424`).
  - Penanganan sinyal `close-request` pada GTK4 dengan `hide()` dan `return True` untuk mencegah *window destruction crash*.
- [x] **Standar Integrasi Desktop Industri (Single Menu Item):**
  - Entri menu Linux Mint disatukan menjadi 1 entri elegan dengan Desktop Action klik-kanan "Pengaturan Mint Island".
  - Re-aktivasi menu saat background daemon berjalan otomatis menampilkan jendela pengaturan via IPC `GApplication`.
- [x] **Paket Rilis Diperbarui:**
  - Biner mesin ELF C Nuitka (`build/bin/mint-island`) dan paket Debian (`dist/mint-island_1.1.0_amd64.deb` & `dist/mint-island_1.1.0_all.deb`) diperbarui dengan seluruh refaktor kode bersih di atas.


