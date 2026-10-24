# 🤖 AGENTS.MD: MASTER INSTRUCTION FOR AI AGENT

**Proyek:** Mint-Island (Dynamic Island Native untuk Linux Mint 22.3 Cinnamon)  
**Lingkungan Target:** Linux Mint 22.3 Zena (Ubuntu 24.04 Noble LTS base), Cinnamon DE, X11 Display Server, Python 3.12, GTK4/Libadwaita.  
**Tujuan Pengguna:** Pengguna baru saja berpindah dari Windows ke Linux demi mencari sistem yang **ringan, hemat baterai, dan responsif**. Aplikasi Dynamic Island ini harus berjalan native, ringan (<45 MB RAM, 0% CPU idle), auto-start saat reboot, dan memiliki menu kontrol yang mudah diatur.

---

## 📌 Pedoman Perilaku AI Agent

Setiap kali Anda mengerjakan repositori ini, Anda WAJIB:
1. **Membaca Dokumen Desain:** Periksa selalu [RANCANGAN_DYNAMIC_ISLAND_LINUX_MINT.md](file:///home/yusuf/projekan/lapatop%20app/RANCANGAN_DYNAMIC_ISLAND_LINUX_MINT.md) dan [ROADMAP.md](file:///home/yusuf/projekan/lapatop%20app/ROADMAP.md).
2. **Kepatuhan Aturan:**
   - Patuhi aturan penulisan kode di [.agents/rules/01_coding_standards.md](file:///home/yusuf/projekan/lapatop%20app/.agents/rules/01_coding_standards.md).
   - Patuhi batasan performa di [.agents/rules/02_lightweight_constraints.md](file:///home/yusuf/projekan/lapatop%20app/.agents/rules/02_lightweight_constraints.md).
   - Patuhi alur kerja bertahap di [.agents/rules/03_phases_workflow.md](file:///home/yusuf/projekan/lapatop%20app/.agents/rules/03_phases_workflow.md).
3. **Eksekusi Bertahap (Phased Development):** Kerjakan hanya 1 fase yang diminta pengguna sampai selesai dan teruji. Jangan melompat ke fase berikutnya tanpa persetujuan pengguna.
4. **Perbarui Dokumentasi:** Setiap selesai mengimplementasikan fitur, perbarui status di [ROADMAP.md](file:///home/yusuf/projekan/lapatop%20app/ROADMAP.md) dan catat detail di [CHANGELOG.md](file:///home/yusuf/projekan/lapatop%20app/CHANGELOG.md).

---

## 🗺️ Panduan Perintah / Prompt Pengguna per Fase

Pengguna dapat menyalin (*copy-paste*) prompt di bawah ini ke AI kapan saja untuk melanjutkan pekerjaan fase demi fase:

### 🔹 Prompt untuk Fase 1 (Pondasi Window & Autostart)
```text
Halo AI, tolong kerjakan FASE 1: Buat pondasi jendela utama Dynamic Island menggunakan Python GTK4 di Linux Mint (jendela kapsul transparan di atas layar, always-on-top, borderless) beserta sistem konfigurasi config.json dan mekanisme autostart saat laptop dinyalakan ulang. Pastikan kodenya bisa diuji langsung.
```

### 🔹 Prompt untuk Fase 2 (Hardware Event Listeners & HUD)
```text
Halo AI, tolong kerjakan FASE 2: Integrasikan event listener D-Bus untuk deteksi perubahan volume audio, kecerahan layar, dan status charger baterai (UPower). Buat animasi HUD mekar selama 3 detik lalu mengecil kembali secara halus.
```

### 🔹 Prompt untuk Fase 3 (YouTube & Media Player + Lirik Karaoke)
```text
Halo AI, tolong kerjakan FASE 3: Integrasikan pemutar musik dari YouTube (browser) dan Spotify via MPRIS D-Bus. Tambahkan modul lirik lagu real-time (LRCLIB API) yang tersinkronisasi detik demi detik seperti karaoke, baik di kapsul atas maupun saat kartu diklik terbuka.
```

### 🔹 Prompt untuk Fase 4 (Menu Pengaturan & Tray Icon)
```text
Halo AI, tolong kerjakan FASE 4: Buat Menu Pengaturan lengkap (GUI Control Panel menggunakan Libadwaita) dan ikon di panel baki sistem (Tray Icon). Pastikan saklar ON/OFF dan pengaturan modul berfungsi mengubah tampilan pulau secara instan.
```

### 🔹 Prompt untuk Fase 5 (Optimasi Resource & Script Installer)
```text
Halo AI, tolong kerjakan FASE 5: Lakukan pengujian akhir konsumsi RAM dan CPU, pastikan sangat ringan (<40 MB RAM, 0% CPU idle), uji ketahanan restart laptop, dan buatkan skrip instalasi otomatis satu perintah (install.sh).
```

---

## 🛠️ Stack Teknologi & Perintah Verifikasi

- **Jalankan Aplikasi Langsung:**
  ```bash
  python3 /home/yusuf/projekan/lapatop\ app/mint_island/main.py
  ```
- **Periksa Konsumsi Memori & CPU:**
  ```bash
  ps -o pid,user,%cpu,%mem,rss,comm -C python3 | grep main.py
  ```
- **Periksa MPRIS Browser / YouTube Aktif:**
  ```bash
  python3 -c "import dbus; bus=dbus.SessionBus(); print([n for n in bus.list_names() if 'mpris' in n])"
  ```
- **Periksa File Autostart:**
  ```bash
  cat ~/.config/autostart/mint-island.desktop
  ```
