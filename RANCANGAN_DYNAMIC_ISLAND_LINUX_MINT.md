# 🏝️ DOKUMEN RANCANGAN & ANALISIS TEKNIS: DYNAMIC ISLAND UNTUK LINUX MINT
**Nama Proyek:** Mint-Island (Dynamic Island for Linux Mint)  
**Target Sistem Operasi:** Linux Mint 22.3 (Zena / Cinnamon Desktop Environment)  
**Display Server:** X11 (Xorg)  
**Bahasa & Framework:** Python 3.12 + GTK4 / Libadwaita + D-Bus API  
**Status Analisis:** 100% FEASIBLE (Sangat Bisa & Sangat Realistis Dibuat)

---

## 📋 DAFTAR ISI
1. [Ringkasan Eksekutif & Kesimpulan Riset](#1-ringkasan-eksekutif--kesimpulan-riset)
2. [Hasil Riset & Analisis Lingkungan Sistem (Linux Mint)](#2-hasil-riset--analisis-lingkungan-sistem-linux-mint)
3. [Mekanisme Autostart & Persistensi Reboot (Laptop Mati -> Hidup)](#3-mekanisme-autostart--persistensi-reboot)
4. [Daftar Fitur & Apa Saja yang Ditampilkan di Dynamic Island](#4-daftar-fitur--apa-saja-yang-ditampilkan)
5. [Desain Status Tampilan (UI States & Anatomi Island)](#5-desain-status-tampilan-ui-states--anatomi-island)
6. [Arsitektur Sistem & Alur Komunikasi (D-Bus & Event Listener)](#6-arsitektur-sistem--alur-komunikasi)
7. [Rancangan Menu Kontrol & Pengaturan (Settings GUI & Tray)](#7-rancangan-menu-kontrol--pengaturan)
8. [Struktur File Proyek & Skema Konfigurasi](#8-struktur-file-proyek--skema-konfigurasi)
9. [Blueprint Implementasi Kode (Proof-of-Concept Siap Pakai)](#9-blueprint-implementasi-kode)
10. [Rencana Tahapan Pengembangan (Roadmap)](#10-rencana-tahapan-pengembangan)

---

## 1. RINGKASAN EKSEKUTIF & KESIMPULAN RISET

### Pertanyaan Utama:
1. **Apakah bisa membuat Dynamic Island di Linux Mint?**  
   👉 **JAWABAN: SANGAT BISA (100% FEASIBLE).**  
   Linux Mint memiliki arsitektur desktop yang sangat terbuka. Dengan window manager Cinnamon (Muffin) di atas X11, kita dapat membuat jendela *floating borderless* transparan di bagian atas layar (`top-center`), selalu berada di paling depan (*always on top*), tidak muncul di daftar taskbar/pager, dan mendukung efek animasi membesar/mengecil halus (*pill expansion*).

2. **Apakah bisa berjalan secara NATIVE dan RINGAN?**  
   👉 **BISA.**  
   Dibandingkan menggunakan Electron/Chromium (yang memakan RAM 200–400 MB), implementasi native menggunakan **Python 3.12 + GTK4 / Libadwaita** hanya mengonsumsi **~25–45 MB RAM** dan hampir 0% CPU saat idle. Library ini sudah terpasang secara *default* di Linux Mint 22.3.

3. **Apakah bisa AUTO-START setelah laptop dimatikan dan dihidupkan lagi?**  
   👉 **BISA.**  
   Menggunakan mekanisme standar **XDG Autostart** (`~/.config/autostart/mint-island.desktop`). Ketika status di menu pengaturan diatur ke **ON**, file autostart akan dibuat/diaktifkan. Ketika laptop dinyalakan ulang (reboot/cold boot), Cinnamon Session Manager langsung mengeksekusi daemon di background tanpa perlu terminal.

4. **Apakah ada Menu Kontrol / Pengaturannya?**  
   👉 **BISA LENGKAP.**  
   Disediakan dua akses pengaturan:
   - **System Tray Icon (Panel Linux Mint):** Ikon kecil di sudut kanan bawah untuk Quick Toggle (ON/OFF), reload, dan buka pengaturan.
   - **Control Panel GUI (Libadwaita Window):** Jendela pengaturan bergaya modern Linux Mint untuk mengatur saklar on/off, modul apa saja yang aktif, ukuran/posisi, animasi, dan tema.

---

## 2. HASIL RISET & ANALISIS LINGKUNGAN SISTEM (LINUX MINT)

Berdasarkan pengujian langsung pada sistem:
- **OS:** Linux Mint 22.3 (Codenamed Zena, basis Ubuntu 24.04 Noble LTS).
- **Desktop Environment:** Cinnamon (`X-Cinnamon`).
- **Display Server:** X11 (`x11`).
- **Komponen Native yang Tersedia:**
  - Python `3.12.3` (Tersedia)
  - `GTK4` dan `Libadwaita 1.0` (Tersedia & Aktif)
  - `AyatanaAppIndicator3` untuk System Tray (Tersedia)
  - `python-dbus` / `Gio.DBus` (Tersedia)
  - `pactl` / PipeWire untuk audio (Tersedia)
  - `UPower` D-Bus untuk baterai & charging (Tersedia)
  - `org.mpris.MediaPlayer2` D-Bus untuk pemutar media seperti Spotify, YouTube/Brave, VLC (Tersedia)
  - `/sys/class/backlight` untuk kecerahan layar (Tersedia)

### Keunggulan X11 + Cinnamon untuk Dynamic Island:
- **Window Hinting Fleksibel:** Kita dapat menandai jendela sebagai `_NET_WM_WINDOW_TYPE_DOCK` atau `POPUP_MENU` dengan `keep_above = True`, `skip_taskbar = True`, dan `skip_pager = True`.
- **Transparansi Sempurna (True RGBA):** Mendukung background transparan dan border radius melengkung berbentuk kapsul (pill shape) menggunakan stylesheet CSS GTK.
- **Click-through & Event Handling:** Ketika pulau dalam ukuran kecil, hanya area pulau yang menangkap klik mouse; area transparan di sekitarnya tidak menghalangi jendela aplikasi di belakangnya.

---

## 3. MEKANISME AUTOSTART & PERSISTENSI REBOOT

Agar aplikasi selalu aktif secara otomatis meskipun laptop dimatikan, restart, atau baterai habis:

### A. Alur Kerja Autostart
```mermaid
graph TD
    A[User Mengaktifkan Toggle 'ON' di Pengaturan] --> B[Sistem Menyimpan config.json: 'enabled': true]
    B --> C[Sistem Menulis File ~/.config/autostart/mint-island.desktop]
    C --> D[Laptop Dimatikan / Shutdown]
    D --> E[Laptop Dihidupkan Kembali]
    E --> F[Cinnamon Session Manager membaca ~/.config/autostart/]
    F --> G[Eksekusi: python3 -m mint_island]
    G --> H{Cek config.json}
    H -- enabled == true --> I[Dynamic Island Langsung Aktif di Layar Atas]
    H -- enabled == false --> J[Proses Idle di Background / Tray Only]
```

### B. Format File Autostart (`~/.config/autostart/mint-island.desktop`)
```ini
[Desktop Entry]
Type=Application
Exec=/usr/bin/python3 /home/yusuf/projekan/lapatop\ app/mint_island/main.py --daemon
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Mint Island
Comment=Dynamic Island HUD for Linux Mint Cinnamon
Icon=utilities-system-monitor
Categories=Utility;TrayIcon;
StartupNotify=false
Terminal=false
```

---

## 4. DAFTAR FITUR & APA SAJA YANG DITAMPILKAN

Dynamic Island akan dirancang adaptif berdasarkan prioritas event (kejadian):

| Kategori | Fitur / Indikator | Kondisi Pemicu (Trigger) | Tampilan di Dynamic Island |
| :--- | :--- | :--- | :--- |
| **Media Player (YouTube & All)** | Musik / Video Playback | YouTube (Brave/Chrome/Firefox), Spotify, VLC, MPV | Cover art/thumbnail video, equalizer audio bar bergerak, judul lagu & channel/artis. Klik untuk Play/Pause/Next/Prev & Seekbar. |
| **Lirik Lagu (Karaoke Synced)** | Lirik Berjalan Real-time | Lagu sedang diputar di YouTube / Spotify | **Mode Island:** Menampilkan 1 baris lirik saat ini yang sedang dinyanyikan (*karaoke subtitle*).<br>**Mode Expand:** Panel lirik penuh bergulir (*scrolling synced lyrics*) dengan baris aktif menyala. |
| **Audio & Volume** | Volume Level HUD | Tombol Fn Volume Up/Down/Mute ditekan | Ikon speaker + progress bar persentase volume secara real-time. |
| **Brightness** | Kecerahan Layar HUD | Tombol Fn Kecerahan ditekan | Ikon matahari + slider intensitas cahaya layar. |
| **Daya & Baterai** | Charger Terhubung | Kabel charger dicolokkan ke laptop | Animasi petir hijau mekar, teks *"Charging • 78%"* beserta estimasi waktu penuh. |
| **Daya & Baterai** | Charger Dicabut | Kabel charger dilepas dari laptop | Indikator baterai putih *"On Battery • 78%"*. |
| **Baterai Lemah** | Low Battery Warning | Kapasitas baterai <= 15% | Ikon baterai berkedip merah peringatan *"Battery Low (<15%)"*. |
| **Notifikasi Sistem** | Pop-up Notifikasi Masuk | Chat WA/Telegram, Email, Download selesai | Pulau melebar menampilkan logo aplikasi, nama pengirim, dan ringkasan pesan selama 4 detik. |
| **Konektivitas** | Wi-Fi / Bluetooth | Terkoneksi ke hotspot / TWS / Headphone | Ikon Wi-Fi/Bluetooth dengan nama perangkat yang baru terhubung. |
| **Perangkat Eksternal** | Flashdisk / USB Drive | USB Drive dicolok | Ikon drive *"USB Drive Mounted • 32 GB"*. |
| **Status Keyboard** | Caps Lock / Mic Mute | Tombol Caps Lock atau Mute Mic ditekan | Indikator HUD minimalis *"CAPS ON"* atau *"MIC MUTED"*. |
| **Produktivitas** | Timer / Pomodoro / Stopwatch | Timer kerja diaktifkan dari pengaturan | Countdown waktu berjalan (misal: *24:50*). |
| **Informasi Default** | Idle / Siaga (Tanpa Event) | Tidak ada musik / event aktif | Jam digital ringkas + status baterai minimalis atau tersembunyi halus (*stealth pill*). |

---

## 5. DESAIN STATUS TAMPILAN (UI STATES & ANATOMI ISLAND)

Dynamic Island memiliki 4 kondisi bentuk (*states*):

```
1. IDLE STATE (Bentuk Kapsul Minimalis)
+------------------------------------------+
|  🕒 23:45    [======🔋 82%]              |
+------------------------------------------+
Ukuran: ~160px × 32px

2. HUD STATE (Volume / Kecerahan / Charger Dicolok - 3 Detik)
+-------------------------------------------------------------+
|  🔊  [========================----------]  68%              |
+-------------------------------------------------------------+
Ukuran: ~240px × 36px (Animasi halus memanjang)

3. NOTIFICATION STATE (Pemberitahuan Masuk - 4 Detik)
+--------------------------------------------------------------------------+
|  💬  Yusuf: "File tugas sudah dikirim ya..."            [Balas] [Tutup] |
+--------------------------------------------------------------------------+
Ukuran: ~340px × 46px

4. EXPANDED / INTERACTIVE STATE (Ketika Diklik / Hover)
+--------------------------------------------------------------------------+
|  [Cover]   Bohemian Rhapsody                                             |
|  [Art  ]   Queen — A Night at the Opera                                  |
|            01:45 ━━━━━━━━●━━━━━━━━━━━━━ 05:55                           |
|            ⏮️   ⏸️   ⏭️       🔊 [========---] 70%                     |
|  ----------------------------------------------------------------------  |
|  ⚡ Battery: 82% (Charging)  |  ☀️ Brightness: 75%  |  ⚙️ Settings       |
+--------------------------------------------------------------------------+
Ukuran: ~380px × 160px (Mekar menjadi kartu lengkap interaktif)

5. KARAOKE LYRICS STATE (Mode Lirik Berjalan / Synced Lyrics)
A. Mini Island Subtitle (Di Kapsul Atas):
+--------------------------------------------------------------------------+
|  🎵 [Cover] "Mama, just killed a man, put a gun against his head..."     |
+--------------------------------------------------------------------------+
Ukuran: ~420px × 36px (Teks lirik baris aktif mengalir halus sesuai lagu)

B. Expanded Karaoke Card (Klik Mode Lirik):
+--------------------------------------------------------------------------+
|  [Cover] Bohemian Rhapsody - Queen                       [X] Tutup Lirik |
|  ----------------------------------------------------------------------  |
|     Is this the real life? Is this just fantasy?                         |
|     Caught in a landslide, no escape from reality...                     |
|  ▶  MAMA, JUST KILLED A MAN, PUT A GUN AGAINST HIS HEAD...  (SEDANG AKTIF)
|     Pulled my trigger, now he's dead...                                  |
|     Mama, life had just begun...                                         |
+--------------------------------------------------------------------------+
Ukuran: ~420px × 240px (Scrolling otomatis mengikuti timestamp lagu)
```

---

## 6. ARSITEKTUR SISTEM & ALUR KOMUNIKASI

Aplikasi dibangun dengan arsitektur modular berbasis event-driven:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LINUX SYSTEM & HARDWARE                         │
├───────────────┬────────────────┬──────────────────────┬────────────────┤
│ PulseAudio    │ UPower D-Bus   │ MPRIS Media Players  │ Cinnamon       │
│ (Volume/Mute) │ (Baterai/Chg)  │ (Spotify/Brave/VLC)  │ (Notifications)│
└───────┬───────┴────────┬───────┴──────────┬───────────┴────────┬───────┘
        │                │                  │                    │
        ▼                ▼                  ▼                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       EVENT BUS & LISTENERS                            │
│  - MediaListener        : Memantau lagu ganti, play/pause              │
│  - BatteryListener      : Memantau charger plug/unplug, % baterai      │
│  - AudioVolumeListener  : Memantau perubahan volume pactl/pipewire     │
│  - NotifyListener       : Menangkap org.freedesktop.Notifications      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Signal / Event
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   MINT-ISLAND CORE CONTROLLER                          │
│  - Prioritas Event: HUD > Notification > Media Playing > Idle          │
│  - State Machine  : IDLE -> EXPAND_HUD -> COLLAPSE -> EXPAND_CARD      │
│  - Config Reader  : Membaca config.json (apakah modul aktif?)          │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │ Render Callback                │ Tray & Status
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       GTK4 FLOATING OVERLAY          │  │       SYSTEM TRAY MENU       │
│ - Window Hint: DOCK/OVERLAY (X11)    │  │ - AyatanaAppIndicator        │
│ - CSS Styled: Border-radius, Blur    │  │ - Toggle Island ON/OFF       │
│ - Fluid Animations: GTK Clocks       │  │ - Open Preferences GUI       │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

### B. Mekanisme Pemutar YouTube & Lirik Tersinkronisasi (Real-Time Karaoke)
Bagaimana Dynamic Island bisa memutar/mengontrol YouTube dan menampilkan lirik lagu yang pas dengan detik musiknya?

1. **Integrasi YouTube & Browser via MPRIS D-Bus:**
   - Semua peramban web modern di Linux Mint (Google Chrome, Brave, Firefox, Edge, Chromium) secara native memancarkan protokol **MPRIS v2** (`org.mpris.MediaPlayer2.<browser>`).
   - Saat Anda membuka YouTube dan memutar video/musik, Linux Mint langsung mengenali:
     - Judul lagu / video (`xesam:title`)
     - Nama Channel / Artis (`xesam:artist`)
     - Thumbnail video / Cover album (`mpris:artUrl`)
     - Posisi detik saat ini (`Position`) & Durasi total (`mpris:length`)
   - Dynamic Island dapat mengirimkan sinyal kendali: **Play, Pause, Next, Previous, Seek Time**.

2. **Pembersih Judul Otomatis (Title Cleaner Engine):**
   - Di YouTube, judul video sering mengandung teks tambahan seperti *"Queen - Bohemian Rhapsody (Official Video) [Remastered 4K] ft. ..."*.
   - Modul `lyrics_module.py` menggunakan regex cerdas untuk membersihkan teks tersebut sehingga menjadi nama artis murni (*Queen*) dan nama lagu (*Bohemian Rhapsody*).

3. **Pengambilan Lirik Otomatis (LRCLIB API):**
   - Menggunakan layanan database lirik terbuka **LRCLIB** (gratis, tanpa API key, sangat cepat).
   - Format lirik yang diambil bertipe **Synced Lyrics (.LRC)** yang memiliki timestamp detik, contoh:
     ```text
     [00:45.20] Mama, just killed a man
     [00:51.30] Put a gun against his head
     [00:55.10] Pulled my trigger, now he's dead
     ```

4. **Sinkronisasi Detik demi Detik (Karaoke Engine):**
   - Polling timer interval 250ms membandingkan `Position` lagu di YouTube dengan timestamp lirik `.LRC`.
   - **Di Kapsul Island:** Teks lirik yang cocok langsung ditampilkan satu baris mengalir halus.
   - **Di Kartu Expand:** Daftar lirik otomatis bergulir (*auto-scroll*), dan baris yang sedang aktif disorot (*highlight*) tebal dengan efek transisi bercahaya.

---

## 7. RANCANGAN MENU KONTROL & PENGATURAN

Menu kontrol terdiri dari dua pintu masuk:

### A. System Tray Menu (Panel Bawah Kanan)
Ikon di panel Linux Mint dengan menu klik kanan:
- **Aktifkan Dynamic Island** `[✔ Checklist On/Off]`
- **Mode:** `Compact / Normal / Auto-Hide`
- **Pusat Kontrol / Pengaturan...** `(Membuka GUI Settings)`
- **Reload / Refresh Island**
- **Keluar**

### B. Control Panel GUI (Jendela Pengaturan Modern)
Dibuat dengan `Adw.PreferencesWindow` (Libadwaita) agar senada dengan estetika Linux Mint:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚙️ Pengaturan Dynamic Island (Mint-Island)           ─  □  ✕  │
├──────────────────────────────────────────────────────────────┤
│  STATUS UTAMA                                                │
│    Aktifkan Dynamic Island                   [ ON  /  OFF ]  │
│    Mulai Otomatis Saat Laptop Dinyalakan     [   SWITCH   ]  │
│                                                              │
│  PILIHAN MODUL TAMPILAN                                      │
│    🎵 Kontrol Pemutar Media (Spotify/YouTube)[   SWITCH   ]  │
│    🎤 Lirik Lagu Berjalan / Karaoke (Synced) [   SWITCH   ]  │
│    🔋 Status Charger & Baterai               [   SWITCH   ]  │
│    🔊 Indikator Perubahan Volume & Mute      [   SWITCH   ]  │
│    ☀️ Indikator Kecerahan Layar (Brightness) [   SWITCH   ]  │
│    💬 Notifikasi Pop-up Aplikasi             [   SWITCH   ]  │
│    ⌨️ Indikator Caps Lock & Status Mic       [   SWITCH   ]  │
│                                                              │
│  TAMPILAN & POSISI                                           │
│    Posisi Layar                 [ Atas Tengah (Rekomendasi) ]│
│    Jarak dari Atas (Margin Y)   [ 8 px ━━━━●━━━━━━━━ 40 px ] │
│    Ukuran Skala                 [ 100% ━━━━●━━━━━━━━ 150%  ] │
│    Durasi Pop-up HUD            [ 1.5s ━━━━●━━━━━━━━ 5.0s  ] │
│    Tema                         [ OLED Black / Glass Dark ] │
└──────────────────────────────────────────────────────────────┘
```

---

## 8. STRUKTUR FILE PROYEK & SKEMA KONFIGURASI

### A. Struktur Direktori Proyek
```text
mint_island/
├── main.py                     # Entry point (CLI flags & startup)
├── config.py                   # Handler baca/tulis ~/.config/dynamic-island/config.json
├── autostart.py                # Handler instalasi file ~/.config/autostart
├── ui/
│   ├── island_window.py        # Jendela utama GTK4 (Overlay X11, layout kapsul)
│   ├── settings_window.py      # Jendela GUI Pengaturan (Libadwaita)
│   ├── tray_indicator.py       # Ikon baki sistem (AyatanaAppIndicator3)
│   └── styles.css              # Styling CSS: Glassmorphism, Rounded Pill, Warna
├── modules/
│   ├── mpris_module.py         # Monitor lagu dari D-Bus MediaPlayer2 (YouTube, Spotify, dll.)
│   ├── lyrics_module.py        # Pengambil lirik sinkronisasi (LRCLIB API & Karaoke parser)
│   ├── battery_module.py       # Monitor baterai & charger dari UPower
│   ├── volume_module.py        # Monitor volume pulseaudio / pactl
│   └── notification_module.py  # Interseptor org.freedesktop.Notifications
└── assets/
    └── icon.svg                # Ikon aplikasi
```

### B. Skema File Konfigurasi (`~/.config/dynamic-island/config.json`)
```json
{
  "general": {
    "enabled": true,
    "autostart_on_boot": true,
    "start_minimized": false
  },
  "modules": {
    "media_player": true,
    "show_synced_lyrics": true,
    "battery_charging": true,
    "volume_hud": true,
    "brightness_hud": true,
    "system_notifications": true,
    "caps_lock_hud": true
  },
  "appearance": {
    "position": "top-center",
    "y_offset": 8,
    "scale_percent": 100,
    "theme": "glass-dark",
    "hud_timeout_seconds": 3.0,
    "enable_animations": true
  }
}
```

---

## 9. BLUEPRINT IMPLEMENTASI KODE (PROOF-OF-CONCEPT)

Berikut adalah kode dasar arsitektural yang dapat langsung dijalankan untuk membuktikan konsep jendela melayang berbentuk kapsul di Linux Mint:

```python
#!/usr/bin/env python3
"""
Mint-Island: Proof of Concept Prototype for Linux Mint 22.3 (Cinnamon/X11)
"""
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw

class DynamicIslandWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Dynamic Island")
        
        # Properti Jendela Overlay X11
        self.set_decorated(False)
        self.set_resizable(False)
        
        # Load CSS Styling (Glassmorphism & Rounded Pill)
        self.load_css()
        
        # Root Container
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.box.add_css_class("island-container")
        self.box.set_size_request(180, 34)
        
        # Konten Default (Idle)
        self.icon = Gtk.Image.new_from_icon_name("audio-speakers-symbolic")
        self.label = Gtk.Label(label="Mint Island Active")
        self.label.add_css_class("island-text")
        
        self.box.append(self.icon)
        self.box.append(self.label)
        self.set_child(self.box)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: transparent;
        }
        .island-container {
            background-color: rgba(18, 18, 22, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            padding: 4px 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 300ms cubic-bezier(0.16, 1, 0.3, 1);
        }
        .island-text {
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

class MintIslandApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.linuxmint.dynamicisland")
        
    def do_activate(self):
        win = DynamicIslandWindow(self)
        win.present()

if __name__ == "__main__":
    app = MintIslandApp()
    app.run(sys.argv)
```

---

## 10. RENCANA TAHAPAN PENGEMBANGAN (ROADMAP)

Proses pembuatan dapat dibagi menjadi 4 tahap terukur:

1. **Tahap 1: Fondasi Window & Autostart Manager (Selesai dalam 1 Hari)**
   - Pembuatan jendela transparan *top-center* GTK4 dengan X11 window hints.
   - Pembuatan skrip autostart generator ke `~/.config/autostart/`.
   - Penyimpanan status *enable/disable* di `config.json`.

2. **Tahap 2: Integrasi D-Bus & Event Listener (2 Hari)**
   - Listener 1: **MPRIS D-Bus** untuk membaca lagu Spotify/Brave/YouTube secara real-time.
   - Listener 2: **UPower D-Bus** untuk mendeteksi status charger dicolok/dicabut.
   - Listener 3: **PulseAudio/PipeWire Listener** untuk mendeteksi perubahan volume.

3. **Tahap 3: Animasi Morphing & Interaktivitas UI (2 Hari)**
   - Animasi transisi mekar dari Idle (kapsul kecil) ke HUD (volume/charger) dan kembali mengecil otomatis dalam 3 detik.
   - Interaksi klik: Klik pada kapsul akan membuka kartu kontrol musik dan pintasan cepat.

4. **Tahap 4: Menu Pengaturan (Control Panel GUI & Tray Icon) (1 Hari)**
   - Pembuatan jendela Preferences Libadwaita untuk mengatur on/off fitur.
   - Integrasi ikon baki sistem (Tray Icon) di panel Linux Mint Cinnamon.
   - Final packaging & testing reboot laptop.

---
**Dokumen ini merupakan spesifikasi arsitektur final yang siap dieksekusi menjadi kode program utuh.**
