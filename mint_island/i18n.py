"""
Internationalization (i18n) Engine for Mint-Island
Provides bilingual translations (Indonesian & English) with auto-detection.
"""
import os
import locale
from mint_island.config import config_manager

TRANSLATIONS = {
    # General / Window Titles
    "Mint-Island Settings": {
        "id": "Pengaturan Mint-Island",
        "en": "Mint-Island Settings"
    },
    "Settings": {
        "id": "Pengaturan",
        "en": "Settings"
    },
    "About &amp; Community": {
        "id": "Tentang &amp; Komunitas",
        "en": "About &amp; Community"
    },
    "Mint-Island Desktop": {
        "id": "Mint-Island Desktop",
        "en": "Mint-Island Desktop"
    },
    "Native Dynamic Island for Linux Mint (Cinnamon DE)": {
        "id": "Dynamic Island Native untuk Linux Mint (Cinnamon DE)",
        "en": "Native Dynamic Island for Linux Mint (Cinnamon DE)"
    },
    "Version": {
        "id": "Versi",
        "en": "Version"
    },
    "License": {
        "id": "Lisensi",
        "en": "License"
    },
    "Developer &amp; Maintainer": {
        "id": "Pengembang &amp; Pembuat",
        "en": "Developer &amp; Maintainer"
    },
    "Source Code &amp; Community": {
        "id": "Kode Sumber &amp; Komunitas",
        "en": "Source Code &amp; Community"
    },
    "Contribute, report bugs, or star the project on GitHub": {
        "id": "Kontribusi, laporkan bug, atau berikan bintang di GitHub",
        "en": "Contribute, report bugs, or star the project on GitHub"
    },
    "Visit GitHub": {
        "id": "Kunjungi GitHub",
        "en": "Visit GitHub"
    },
    "Report an Issue": {
        "id": "Laporkan Masalah / Bug",
        "en": "Report an Issue"
    },
    "Submit bug reports or suggest new features": {
        "id": "Kirim laporan kendala atau usulkan fitur baru",
        "en": "Submit bug reports or suggest new features"
    },
    "Open Issues": {
        "id": "Buka GitHub Issues",
        "en": "Open Issues"
    },
    "Developer &amp; Supporter Token": {
        "id": "Token Pengembang &amp; Supporter",
        "en": "Developer &amp; Supporter Token"
    },
    "Optional activation token for developers or project sponsors": {
        "id": "Token aktivasi opsional untuk pengembang atau pendukung proyek",
        "en": "Optional activation token for developers or project sponsors"
    },
    "Community Edition (Full Features Unlocked)": {
        "id": "Edisi Komunitas (Semua Fitur Terbuka Penuh)",
        "en": "Community Edition (Full Features Unlocked)"
    },
    "Activate Token": {
        "id": "Aktifkan Token",
        "en": "Activate Token"
    },
    "Reset": {
        "id": "Reset",
        "en": "Reset"
    },
    "License &amp; Activation": {
        "id": "Lisensi &amp; Aktivasi",
        "en": "License &amp; Activation"
    },
    "Main Status": {
        "id": "Status Utama",
        "en": "Main Status"
    },
    "Master controls for island and system autostart.": {
        "id": "Kendali master pulau dan autostart sistem.",
        "en": "Master controls for island and system autostart."
    },
    "Enable Dynamic Island": {
        "id": "Aktifkan Dynamic Island",
        "en": "Enable Dynamic Island"
    },
    "Show floating island at top of screen": {
        "id": "Tampilkan pulau melayang di bagian atas layar",
        "en": "Show floating island at top of screen"
    },
    "Start Automatically on Boot": {
        "id": "Mulai Otomatis Saat Laptop Dinyalakan",
        "en": "Start Automatically on Boot"
    },
    "Launch on user login without terminal": {
        "id": "Jalankan otomatis saat login tanpa perlu terminal",
        "en": "Launch on user login without terminal"
    },
    "Interface Language": {
        "id": "Bahasa Antarmuka (Language)",
        "en": "Interface Language"
    },
    "Select display language for island and controls": {
        "id": "Pilih bahasa tampilan untuk pulau dan menu pengaturan",
        "en": "Select display language for island and controls"
    },

    # Display Modules Group
    "Display Modules": {
        "id": "Pilihan Modul Tampilan",
        "en": "Display Modules"
    },
    "Choose features to show on Dynamic Island.": {
        "id": "Pilih fitur yang ingin ditampilkan pada Dynamic Island.",
        "en": "Choose features to show on Dynamic Island."
    },
    "🎵 Media Player Controls (YouTube / Spotify)": {
        "id": "🎵 Kontrol Pemutar Media (YouTube / Spotify)",
        "en": "🎵 Media Player Controls (YouTube / Spotify)"
    },
    "Track detection, play/pause buttons, and seekbar": {
        "id": "Mendeteksi lagu, tombol play/pause, dan durasi seekbar",
        "en": "Track detection, play/pause buttons, and seekbar"
    },
    "🎤 Synced Karaoke Lyrics": {
        "id": "🎤 Lirik Lagu Berjalan / Karaoke Synced",
        "en": "🎤 Synced Karaoke Lyrics"
    },
    "Fetch real-time lyrics synchronized per second": {
        "id": "Mengambil lirik real-time yang tersinkronisasi per detik",
        "en": "Fetch real-time lyrics synchronized per second"
    },
    "⚡ Battery &amp; Charging HUD (UPower)": {
        "id": "⚡ Status Charger &amp; Peringatan Baterai (UPower)",
        "en": "⚡ Battery &amp; Charging HUD (UPower)"
    },
    "Popup on charger connect/disconnect and low battery": {
        "id": "Pop-up saat charger dicolok/dicabut dan baterai lemah",
        "en": "Popup on charger connect/disconnect and low battery"
    },
    "🔊 Volume &amp; Mute HUD Indicator": {
        "id": "🔊 Indikator Perubahan Volume &amp; Mute",
        "en": "🔊 Volume &amp; Mute HUD Indicator"
    },
    "HUD popup slider when volume keys are pressed": {
        "id": "Slider HUD saat tombol volume keyboard ditekan",
        "en": "HUD popup slider when volume keys are pressed"
    },
    "☀️ Screen Brightness HUD": {
        "id": "☀️ Indikator Kecerahan Layar (Brightness)",
        "en": "☀️ Screen Brightness HUD"
    },
    "HUD popup slider when brightness keys are pressed": {
        "id": "Slider HUD saat tombol Fn kecerahan ditekan",
        "en": "HUD popup slider when brightness keys are pressed"
    },
    "🍃 Power Profile Switcher (Daemon)": {
        "id": "🍃 Mode Daya Hemat Baterai (Power Profile)",
        "en": "🍃 Power Profile Switcher (Daemon)"
    },
    "Quick toggle for Power Saver, Balanced, and Performance modes": {
        "id": "Pilihan cepat mode Hemat Daya, Seimbang, dan Performa",
        "en": "Quick toggle for Power Saver, Balanced, and Performance modes"
    },
    "🔔 System Notifications HUD": {
        "id": "🔔 Pop-up Notifikasi Sistem di Pulau",
        "en": "🔔 System Notifications HUD"
    },
    "Display incoming desktop notifications on the island": {
        "id": "Tampilkan notifikasi desktop yang masuk di pulau",
        "en": "Display incoming desktop notifications on the island"
    },
    "🎧 Bluetooth &amp; TWS Headphone HUD": {
        "id": "🎧 Popup Bluetooth &amp; TWS Headphone",
        "en": "🎧 Bluetooth &amp; TWS Headphone HUD"
    },
    "🎧 Bluetooth & TWS Headphone HUD": {
        "id": "🎧 Popup Bluetooth & TWS Headphone",
        "en": "🎧 Bluetooth & TWS Headphone HUD"
    },
    "Display connection status and battery percentage when Bluetooth devices connect": {
        "id": "Tampilkan status koneksi dan persentase baterai saat perangkat Bluetooth terhubung",
        "en": "Display connection status and battery percentage when Bluetooth devices connect"
    },
    "Connected": {
        "id": "Terhubung",
        "en": "Connected"
    },
    "Disconnected": {
        "id": "Terputus",
        "en": "Disconnected"
    },
    "Bluetooth Devices": {
        "id": "Perangkat Bluetooth",
        "en": "Bluetooth Devices"
    },

    # Appearance & Position Group
    "Position &amp; Animation": {
        "id": "Posisi dan Animasi",
        "en": "Position &amp; Animation"
    },
    "Configure vertical offset, screen selection, and HUD timeout.": {
        "id": "Sesuaikan letak posisi vertikal, layar monitor, dan durasi animasi.",
        "en": "Configure vertical offset, screen selection, and HUD timeout."
    },
    "Select Display / Monitor": {
        "id": "Pilih Layar / Monitor",
        "en": "Select Display / Monitor"
    },
    "Choose monitor where Dynamic Island will appear": {
        "id": "Pilih monitor tempat Dynamic Island akan ditampilkan",
        "en": "Choose monitor where Dynamic Island will appear"
    },
    "Top Screen Margin (Y Offset)": {
        "id": "Jarak dari Atas Layar (Margin Y)",
        "en": "Top Screen Margin (Y Offset)"
    },
    "Adjust vertical gap from top edge of monitor": {
        "id": "Atur posisi vertikal pulau dari tepi atas monitor",
        "en": "Adjust vertical gap from top edge of monitor"
    },
    "Compact Micro-Pill Mode (115px)": {
        "id": "Mode Kapsul Ramping (Micro-Pill 115px)",
        "en": "Compact Micro-Pill Mode (115px)"
    },
    "Slim during idle, expands only on mouse hover or track change": {
        "id": "Ramping saat normal, hanya mekar lebar saat kursor hover atau lagu berganti",
        "en": "Slim during idle, expands only on mouse hover or track change"
    },
    "HUD Popup Duration (Seconds)": {
        "id": "Durasi Tampilan HUD (Detik)",
        "en": "HUD Popup Duration (Seconds)"
    },
    "How long volume and battery popups remain visible": {
        "id": "Berapa lama animasi volume/baterai mekar sebelum menciut",
        "en": "How long volume and battery popups remain visible"
    },

    # License Page
    "Pro License Status": {
        "id": "Status Lisensi Pro",
        "en": "Pro License Status"
    },
    "Current Edition": {
        "id": "Edisi Aplikasi",
        "en": "Current Edition"
    },
    "Pro Lifetime License (Active)": {
        "id": "Lisensi Pro Seumur Hidup (Aktif) 🌟",
        "en": "Pro Lifetime License (Active) 🌟"
    },
    "Free Trial / Community Edition": {
        "id": "Edisi Gratis / Uji Coba",
        "en": "Free Trial / Community Edition"
    },
    "All premium features unlocked (Synced Lyrics, Multi-Monitor, Themes)": {
        "id": "Semua fitur premium terbuka (Lirik Karaoke, Multi-Monitor, Tema)",
        "en": "All premium features unlocked (Synced Lyrics, Multi-Monitor, Themes)"
    },
    "Activate your license key to unlock full features": {
        "id": "Aktivasi kunci lisensi untuk membuka semua fitur pro",
        "en": "Activate your license key to unlock full features"
    },
    "Product License Key": {
        "id": "Kunci Lisensi Produk",
        "en": "Product License Key"
    },
    "Enter License Key (e.g. ISL-PRO-XXXX-YYYY-ZZZZ)": {
        "id": "Masukkan Kunci Lisensi (e.g. ISL-PRO-XXXX-YYYY-ZZZZ)",
        "en": "Enter License Key (e.g. ISL-PRO-XXXX-YYYY-ZZZZ)"
    },
    "Activate License": {
        "id": "Aktivasi Lisensi",
        "en": "Activate License"
    },
    "Deactivate": {
        "id": "Deaktivasi",
        "en": "Deactivate"
    },
    "Buy Pro License ($8.00)": {
        "id": "Beli Lisensi Pro ($8.00 / Rp 120.000)",
        "en": "Buy Pro License ($8.00 USD)"
    },
    "Get instant lifetime license key on official store": {
        "id": "Dapatkan kunci lisensi langsung di toko resmi Lemon Squeezy / Gumroad",
        "en": "Get instant lifetime license key on official store"
    },
    "Visit Store": {
        "id": "Buka Toko",
        "en": "Visit Store"
    },

    # Dynamic Island Labels & HUD
    "No media playing": {
        "id": "Tidak ada media diputar",
        "en": "No media playing"
    },
    "Volume": {
        "id": "Volume",
        "en": "Volume"
    },
    "Brightness": {
        "id": "Kecerahan",
        "en": "Brightness"
    },
    "Battery": {
        "id": "Baterai",
        "en": "Battery"
    },
    "Charging": {
        "id": "Mengisi Daya",
        "en": "Charging"
    },
    "Charging (AC)": {
        "id": "Sedang Mengisi Daya (AC)",
        "en": "Charging (AC)"
    },
    "Battery Power": {
        "id": "Daya Baterai",
        "en": "Battery Power"
    },
    "Discharging": {
        "id": "Baterai",
        "en": "Discharging"
    },
    "Battery Low": {
        "id": "Baterai Lemah!",
        "en": "Battery Low!"
    },
    "Fully Charged": {
        "id": "Terisi Penuh",
        "en": "Fully Charged"
    },
    "Full in": {
        "id": "Penuh dalam",
        "en": "Full in"
    },
    "Remaining": {
        "id": "Tersisa",
        "en": "Remaining"
    },
    "Health": {
        "id": "Kesehatan",
        "en": "Health"
    },
    "Ready to detect media...": {
        "id": "Siap mendeteksi lagu...",
        "en": "Ready to detect media..."
    },
    "Lyrics disabled in Settings": {
        "id": "Lirik dinonaktifkan di Pengaturan",
        "en": "Lyrics disabled in Settings"
    },
    "Lyrics not found in database": {
        "id": "Lirik tidak ditemukan di database",
        "en": "Lyrics not found in database"
    },
    "Synchronized lyrics ready": {
        "id": "Lirik tersinkronisasi siap",
        "en": "Synchronized lyrics ready"
    },
    "Power Mode": {
        "id": "Mode Daya",
        "en": "Power Mode"
    },
    "Power Saver": {
        "id": "Hemat Daya",
        "en": "Power Saver"
    },
    "Balanced": {
        "id": "Seimbang",
        "en": "Balanced"
    },
    "Performance": {
        "id": "Performa",
        "en": "Performance"
    },
    "Remaining": {
        "id": "Tersisa",
        "en": "Remaining"
    },
    "Full in": {
        "id": "Penuh dalam",
        "en": "Full in"
    },
    "Health": {
        "id": "Kesehatan",
        "en": "Health"
    },
    "Fully Charged": {
        "id": "Terisi Penuh",
        "en": "Fully Charged"
    }
}

class I18nManager:
    def __init__(self):
        self._current_lang = self._detect_language()

    def _detect_language(self) -> str:
        """Detect language from user config or system locale."""
        cfg_lang = config_manager.get("general", "language", "auto")
        if cfg_lang in ("id", "en"):
            return cfg_lang

        # Detect from OS locale
        try:
            sys_lang = os.environ.get("LANG", "") or locale.getdefaultlocale()[0] or ""
            if sys_lang.lower().startswith("id"):
                return "id"
        except Exception:
            pass

        return "en"

    @property
    def current_lang(self) -> str:
        return self._current_lang

    def get_language(self) -> str:
        return self._current_lang

    def set_language(self, lang: str):
        if lang in ("id", "en"):
            self._current_lang = lang
            config_manager.set("general", "language", lang)

    def translate(self, text: str) -> str:
        """Translates a string into the current active language."""
        if text in TRANSLATIONS:
            lang_dict = TRANSLATIONS[text]
            return lang_dict.get(self._current_lang, lang_dict.get("en", text))
        return text

# Global singleton and shorthand
i18n = I18nManager()

def _(text: str) -> str:
    """Convenient translation helper function."""
    return i18n.translate(text)
