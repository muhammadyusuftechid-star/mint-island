# 📏 Coding Standards & Architecture Rules

## 1. Bahasa & Framework
- **Runtime:** Python 3.12+
- **UI Toolkit:** GTK4 (`gi.repository.Gtk`, `Gdk`) + Libadwaita (`gi.repository.Adw`)
- **System Integration:** D-Bus via Python `dbus` atau `Gio.DBus`
- **Audio Control:** `pactl` / PipeWire via subprocess atau D-Bus
- **Tray Icon:** `gi.repository.AyatanaAppIndicator3` atau AppIndicator bawaan Cinnamon

## 2. Window Management (X11 di Linux Mint / Cinnamon)
- Jendela utama Dynamic Island harus selalu:
  - `set_decorated(False)` (tanpa border titlebar standar).
  - Background window transparan (CSS `background-color: transparent;`).
  - Menolak fokus yang mengganggu window aktif lain (`set_focusable(False)` untuk mode kapsul idle).
  - Selalu di atas (`keep_above` / `always_on_top`).
  - Tidak muncul di taskbar (`skip_taskbar_hint(True)`) dan tidak muncul di Alt-Tab / workspace pager (`skip_pager_hint(True)`).
  - Click-through: Area kosong di luar kapsul tidak boleh menghalangi klik mouse ke aplikasi di belakangnya (menggunakan shape mask X11 / input region GTK).

## 3. Asynchronous & Threading Rules
- **DILARANG** melakukan I/O blocking (seperti download cover art atau HTTP request lirik) di thread utama GTK.
- Semua network request (LRCLIB API, HTTP images) harus berjalan di background thread (`threading.Thread` atau `GLib.ThreadPool`) dan hasilnya dikirim kembali ke UI via `GLib.idle_add()`.
- Hindari perulangan `while True: time.sleep(...)`. Gunakan `GLib.timeout_add()` untuk polling berkala jika event-driven tidak tersedia.

## 4. Keamanan & Penanganan Error (Robustness)
- Jika peramban atau player ditutup saat lagu berjalan, modul MPRIS harus menangani pemutusan D-Bus dengan *graceful* tanpa crash.
- Jika API lirik tidak menemukan lirik lagu (404), tampilkan status *fallback* ("Lirik tidak ditemukan") tanpa error di console.
- Konfigurasi JSON (`config.json`) harus divalidasi dengan nilai default jika file corrupt atau belum ada.
