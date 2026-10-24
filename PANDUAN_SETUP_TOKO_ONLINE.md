# 🛍️ PANDUAN LENGKAP SETUP TOKO ONLINE KOMERSIAL: MINT-ISLAND

Panduan komprehensif ini dirancang khusus untuk Anda sebagai kreator/pengembang di Indonesia yang ingin menjual produk perangkat lunak desktop Linux **Mint-Island Pro** ke pasar global maupun lokal secara legal, otomatis, dan tanpa pusing urusan birokrasi pajak lintas negara.

---

## 📌 1. Mengapa Menggunakan "Merchant of Record" (MoR)?

Jika Anda menjual langsung menggunakan payment gateway biasa (seperti Midtrans, Stripe standar, atau PayPal personal):
- ⚠️ Anda diwajibkan secara hukum untuk mendaftar dan menyetorkan pajak **EU VAT (19-27%)**, **UK VAT (20%)**, dan **US State Sales Tax** ke masing-masing otoritas pajak negara pembeli.
- ⚠️ PayPal personal rawan terkena suspend/hold dana hingga 180 hari jika mendadak menerima lonjakan transaksi software internasional.

### Solusi Terbaik: **Lemon Squeezy** atau **Gumroad**
Keduanya bertindak sebagai **Merchant of Record (MoR)**:
- ✅ **Pajak Global Otomatis:** Lemon Squeezy/Gumroad menagih, memungut, dan menyetorkan VAT/Sales Tax ke seluruh dunia atas nama mereka sendiri.
- ✅ **Sistem Lisensi Terintegrasi:** Langsung menyediakan API License Key resmi (menghasilkan kode kunci unik otomatis per pembeli).
- ✅ **Metode Pembayaran Lengkap:** Menerima Kartu Kredit/Debit (Visa, Mastercard, Amex), Apple Pay, Google Pay, dan PayPal.
- ✅ **Legal untuk WNI:** Mendukung pencairan dana langsung ke rekening bank lokal di Indonesia atau akun Wise / PayPal.

---

## 🚀 2. Panduan Langkah demi Langkah di Lemon Squeezy (Rekomendasi Utama)

Lemon Squeezy adalah platform paling modern dan ramah pengembang software (dikelola oleh Stripe).

### Langkah 2.1: Pendaftaran Akun Toko
1. Buka [https://www.lemonsqueezy.com](https://www.lemonsqueezy.com) lalu klik **Get Started**.
2. Masukkan nama toko Anda, misalnya: `Mint-Island Software` atau `LinuxMintTools`.
3. Verifikasi email dan isi kuesioner onboarding:
   - **Type of product:** Digital Software / Desktop Application.
   - **Target Audience:** Linux Mint, Ubuntu, and Desktop Linux Enthusiasts.
   - **Country:** Indonesia.

### Langkah 2.2: Pengaturan Pencairan Dana (Payouts ke Rekening Indonesia)
1. Buka menu **Settings** → **Payouts**.
2. Pilih metode payout:
   - **Opsi A (Paling Disukai & Rate Terbaik): Wise Business / Personal (USD Account)**
     - Dapatkan nomor rekening ACH / Routing number USD dari akun Wise Anda.
     - Transfer dari Lemon Squeezy ke Wise gratis atau berbiaya minimal ($0 - $1).
     - Dari Wise, Anda bisa menukar ke Rupiah (IDR) dan mencairkan ke BCA/Mandiri/BRI/BSI secara instan dengan kurs tengah terbaik.
   - **Opsi B: PayPal Account**
     - Hubungkan alamat email PayPal aktif Anda. Lemon Squeezy akan mentransfer dana setiap 2 minggu atau setiap bulan secara otomatis.
   - **Opsi C: Direct Bank Transfer (Stripe Payouts)**
     - Masukkan nama bank lokal Anda di Indonesia (misal: Bank Central Asia / Bank Mandiri) beserta nomor rekening dan kode SWIFT bank.

### Langkah 2.3: Membuat Produk "Mint-Island Pro Lifetime"
1. Masuk ke dashboard Lemon Squeezy → klik **Store** → **Products** → **New Product**.
2. Isi informasi produk:
   - **Product Name:** `Mint-Island Pro Lifetime (Linux Mint & Ubuntu)`
   - **Description:**
     ```markdown
     Native, ultra-lightweight Dynamic Island floating HUD for Linux Mint 22.3 Cinnamon & Ubuntu 24.04 LTS.
     
     🌟 What's Included in Pro:
     - Real-Time Synced Karaoke Lyrics (LRCLIB API with YouTube, Spotify, VLC)
     - Dynamic Multi-Monitor Selector (Primary HDMI + Laptop eDP)
     - Offline Lyrics Caching (~/.cache/mint-island/lyrics/)
     - Standalone High-Speed C/ELF Binary & Native Debian Package (.deb)
     - Valid for up to 3 Personal Computers
     - Free Lifetime Updates & Priority GitHub Support
     
     Technical Specs:
     - < 45 MB RAM Footprint
     - 0.0% Idle CPU Usage
     - 100% Native GTK4 & Libadwaita (No Electron bloat)
     ```
   - **Pricing Model:** `Single payment` (Satu kali bayar selamanya, no subscription).
   - **Price:** `$8.00 USD` (Bisa mengaktifkan *Purchasing Power Parity* / PPP Diskon 40% khusus pembeli regional Indonesia / Asia Tenggara jika diinginkan).
   - **Tax Category:** `Software (Digital Goods - Downloadable)`.

### Langkah 2.4: Mengaktifkan Fitur License Keys (Kunci Lisensi)
1. Pada halaman edit produk, scroll ke bagian **License Keys**.
2. Centang **Generate license keys**.
3. Atur konfigurasi aktivasi:
   - **Activation Limit:** `3` (Mengizinkan pembeli mengaktifkan lisensi di hingga 3 laptop/PC mereka).
   - **Key prefix:** `ISL-PRO-` (Format kunci akan otomatis menjadi: `ISL-PRO-XXXX-YYYY-ZZZZ`).
   - Kunci ini terhubung langsung dengan modul verifikasi [mint_island/license.py](file:///home/yusuf/projekan/lapatop%20app/mint_island/license.py) yang sudah kita buat!

### Langkah 2.5: Mengunggah File Digital (Files for Download)
Pada bagian **Files for download**, unggah file artefak yang telah kita kompilasi:
1. `mint-island_1.1.0_amd64.deb` (Paket installer Debian native untuk Linux Mint 22.3).
2. `mint-island-bin.tar.gz` (Binary C/ELF standalone kompilasi Nuitka).
3. `INSTALL_AND_LICENSE_GUIDE.txt` (File teks panduan aktivasi).

---

## 🍃 3. Alternatif: Setup Menggunakan Gumroad

Jika Anda ingin alternatif selain Lemon Squeezy, **Gumroad** juga merupakan pilihan populer.

1. Buka [https://gumroad.com](https://gumroad.com) dan buat akun.
2. Tambahkan produk baru: **Digital Product**.
3. Masukkan harga: `$8.00`.
4. Pada tab **Content**, centang **Generate a unique license key per sale**.
5. Unggah file `.deb` dan installer.
6. Pada menu **Payout**, pilih transfer ke akun PayPal atau rekening Bank via Stripe Connect.

---

## ✉️ 4. Template Email Otomatis untuk Pembeli (Order Confirmation)

Kustomisasi email konfirmasi di menu **Settings** → **Email Notifications**:

```text
Subject: Your Mint-Island Pro License Key & Download Link 🚀

Hi {customer_name},

Thank you for supporting independent open-source Linux software! 
Your purchase of Mint-Island Pro Lifetime is confirmed.

🔑 YOUR LICENSE KEY:
{license_key}
(Valid for activation on up to 3 personal computers)

📥 DOWNLOAD & INSTALLATION:
You can download your Debian package (.deb) and binary directly from your Lemon Squeezy library:
{download_link}

⚡ HOW TO ACTIVATE:
1. Install Mint-Island:
   sudo dpkg -i mint-island_1.1.0_amd64.deb

2. Activate your Pro features via Terminal:
   mint-island --activate {license_key}

3. Or via GUI:
   Open "Mint-Island Control Panel" from your application menu, 
   navigate to "Lisensi & Aktivasi", paste your key, and click "Aktifkan Lisensi Pro".

Enjoy your native Dynamic Island on Linux Mint! If you have any feedback or questions, 
reply directly to this email or open an issue on our GitHub.

Best regards,
Yusuf
Developer of Mint-Island
```

---

## 🛡️ 5. Kebijakan Refund & Kepuasan Pelanggan (14-Day Guarantee)

Komunitas Linux sangat menghargai integritas dan transparansi. Terapkan SOP ini:
- **Jaminan 14 Hari Uang Kembali:** Jika aplikasi mengalami konflik dengan konfigurasi monitor tertentu atau pengguna tidak puas, kembalikan uangnya 100% tanpa argumen berbelit-belit.
- Di dashboard Lemon Squeezy, Anda cukup klik tombol **Refund Order** pada pesanan yang bersangkutan. Lisensi pengguna akan otomatis dinonaktifkan (`revoked`).

---

## 📈 6. Target Penjualan & Proyeksi Finansial

| Target Penjualan | Volume Pembeli | Pendapatan Kotor (Gross) | Potongan Platform (~5% + $0.5) | Estimasi Bersih Masuk Rekening |
| :--- | :--- | :--- | :--- | :--- |
| **Bulan 1 (Peluncuran)** | 50 Lisensi | $400.00 USD | ~$45.00 USD | **± Rp 5.600.000,-** |
| **Bulan 2 - 3 (Stabil)** | 100 Lisensi / bln | $800.00 USD | ~$90.00 USD | **± Rp 11.200.000,- / bln** |
| **Target 1 Tahun** | 1.000 Lisensi | $8.000.00 USD | ~$900.00 USD | **± Rp 112.000.000,-** |

*Catatan: Pasar Linux Mint global memiliki jutaan pengguna aktif harian yang haus akan kustomisasi modern namun benci bloatware Electron. Kombinasi harga terjangkau ($8 sekali bayar) dan performa native <45MB RAM memiliki conversion rate tinggi.*
