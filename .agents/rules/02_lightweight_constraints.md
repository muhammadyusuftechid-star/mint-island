# ⚡ Lightweight & Performance Constraints

Pengguna berpindah dari Windows ke Linux demi efisiensi dan performa yang ringan. Semua kode yang ditulis untuk proyek ini HARUS mematuhi batasan performa berikut:

## 1. Batasan Penggunaan Memori (RAM)
- **Target Maksimal:** Resident Set Size (RSS) **< 45 MB** dalam kondisi normal.
- **Cache Management:**
  - Thumbnail cover lagu dibatasi maksimal 128x128 px di memori.
  - Cache gambar cover di memori maksimal menyimpan 5 cover terakhir. Hapus objek pixbuf lama saat berganti lagu.
  - Lirik lagu bertipe teks dibersihkan dari RAM saat pemutar lagu berhenti (*Stopped*).

## 2. Batasan Penggunaan Prosesor (CPU)
- **Kondisi Idle (Siaga):** Penggunaan CPU **0.0% – 0.1%**.
- **Kondisi Animasi (Mekar):** Penggunaan CPU maksimal **1.5% – 2.5%** selama durasi transisi (maksimal 300ms).
- **Aturan Eksekusi:**
  - JANGAN gunakan looping `while True` polling yang memeriksa status tanpa jeda.
  - Gunakan sinyal push D-Bus untuk event hardware (Volume, Baterai, Player status).
  - Untuk timer karaoke lirik, jalankan polling `GLib.timeout_add(250, ...)` HANYA saat pemutar media berstatus `Playing`. Matikan timer saat lagu di-*Pause* atau di-*Stop*.

## 3. Efisiensi Baterai Laptop
- Tidak menggunakan Webview, Electron, atau animasi 3D berkepanjangan.
- Jendela UI tidak boleh melakukan re-draw jika tidak ada perubahan nilai/state.
- Gunakan native GTK CSS transitions (`transition: all 250ms cubic-bezier(...)`).

## 4. Ukuran Disk & Dependensi
- Gunakan library bawaan Linux Mint (Python 3.12, PyGObject, Libadwaita, AyatanaAppIndicator, UPower, pactl).
- Jangan menambah dependensi berat pihak ketiga (hindari Node.js, Chromium, Qt besar, dll).
- Ukuran total direktori aplikasi harus **< 5 MB** (di luar cache sementara).
