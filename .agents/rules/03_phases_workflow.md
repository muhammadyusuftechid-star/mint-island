# 🧭 Phases & Development Workflow Rules

Agar pengembangan proyek terarah, terstruktur, dan mudah dipandu oleh pengguna, AI Agent yang mengerjakan repositori ini WAJIB mematuhi aturan tahapan berikut:

## 1. Prinsip Eksekusi Per Fase
1. **Satu Fase dalam Satu Waktu:** Jangan mengerjakan fitur dari fase berikutnya sebelum fase saat ini selesai dan diverifikasi.
2. **Pengujian Mandiri (Self-Validation):** Setiap selesai mengimplementasikan sebuah fase, jalankan script pengujian atau jalankan aplikasi secara langsung di background untuk memastikan tidak ada sintaks error atau crash.
3. **Pembaruan Dokumen:** Setiap fase selesai, perbarui checklist di `ROADMAP.md` dan catat rincian perubahan di `CHANGELOG.md`.

## 2. Struktur Pembagian 5 Fase Pengembangan
- **Fase 1: Core Foundation & Autostart Manager**
  - Jendela melayang GTK4/X11 (kapsul rounded, transparan, top-center, always on top).
  - Skema konfigurasi `config.json` & skrip autostart generator `~/.config/autostart/`.
- **Fase 2: Hardware Event Listeners (Volume, Brightness, Battery HUD)**
  - D-Bus UPower (deteksi charger & low battery).
  - PipeWire / `pactl` listener (volume popup).
  - Animasi memanjang 3 detik lalu kembali menciut otomatis.
- **Fase 3: Media Player (YouTube & Local) + Karaoke Synced Lyrics Engine**
  - MPRIS listener untuk Brave/Chrome/Firefox/Spotify.
  - Modul lirik LRCLIB dengan subtitle satu baris di kapsul dan panel gulir lirik di mode expand.
- **Fase 4: Menu Pengaturan (Control Panel GUI) & System Tray Icon**
  - Tray icon di panel bawah kanan Linux Mint.
  - Jendela preferensi Libadwaita untuk mengubah konfigurasi secara visual.
- **Fase 5: Optimasi Resource, Uji Reboot, & Script Installer**
  - Pengujian konsumsi RAM & CPU idle.
  - Skrip instalasi satu perintah (`install.sh`).
  - Uji ketahanan saat laptop restart.
