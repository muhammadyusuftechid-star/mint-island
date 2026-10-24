#!/usr/bin/env bash
# ==============================================================================
# Mint-Island: Automatic Installer Script for Linux Mint 22.3 Cinnamon
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/mint_island/main.py"
ICON_SRC="$SCRIPT_DIR/mint_island/assets/mint-island.svg"

BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "=========================================================="
echo "🏝️  Menginstal Mint-Island (Dynamic Island Linux Mint)..."
echo "=========================================================="

# 1. Pastikan direktori tujuan ada
mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR" "$AUTOSTART_DIR"

# 2. Beri izin eksekusi pada script utama
chmod +x "$MAIN_PY"

# 3. Salin ikon aplikasi
if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$ICON_DIR/mint-island.svg"
    echo "✔ Ikon aplikasi terpasang di $ICON_DIR/mint-island.svg"
fi

# 4. Pasang Executable / CLI di ~/.local/bin/mint-island
ln -sfn "$MAIN_PY" "$BIN_DIR/mint-island"
echo "✔ Skrip Python aktif dipasang ke $BIN_DIR/mint-island"

# 5. Buat Desktop Entry untuk Menu Aplikasi (Standar Industri: 1 Ikon + Desktop Actions)
rm -f "$APP_DIR/mint-island-settings.desktop"
cat <<EOF > "$APP_DIR/mint-island.desktop"
[Desktop Entry]
Type=Application
Name=Mint Island
GenericName=Dynamic Island HUD & Controls
Comment=Native Dynamic Island floating notch and control panel for Linux Mint
Exec="$BIN_DIR/mint-island" --daemon
Icon=mint-island
Terminal=false
Categories=Utility;Settings;AudioVideo;
Keywords=island;dynamic;notch;music;volume;lirik;hud;mint;pulau;karaoke;settings;pengaturan;preferences;kontrol;
StartupNotify=true
Actions=Settings;

[Desktop Action Settings]
Name=Pengaturan Mint Island
Name[en]=Mint Island Settings
Exec="$BIN_DIR/mint-island" --settings
EOF

echo "✔ Pintasan Menu Aplikasi dibuat di $APP_DIR/mint-island.desktop"

# 6. Pasang Mekanisme Autostart saat laptop dinyalakan/reboot
"$MAIN_PY" --autostart-enable >/dev/null 2>&1
echo "✔ Autostart berhasil diaktifkan di $AUTOSTART_DIR/mint-island.desktop"

# 7. Refresh database desktop & reload Cinnamon menu
update-desktop-database "$APP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

# Beritahu Cinnamon untuk menyegarkan menu aplikasi secara instan
python3 -c "
import dbus
try:
    bus = dbus.SessionBus()
    obj = bus.get_object('org.Cinnamon', '/org/Cinnamon')
    cin = dbus.Interface(obj, 'org.Cinnamon')
    cin.ReloadXlet('menu@cinnamon.org', 'APPLET')
    cin.Eval('imports.gi.CMenu.Tree.new(\"cinnamon-applications.menu\", imports.gi.CMenu.TreeFlags.NONE).load_sync()')
except Exception:
    pass
" 2>/dev/null || true

# 8. Hentikan instance lama jika ada, lalu jalankan instance baru
pkill -f "mint_island/main.py" 2>/dev/null || true
pkill -f "mint-island" 2>/dev/null || true
setsid "$BIN_DIR/mint-island" --daemon >/dev/null 2>&1 &

echo "=========================================================="
echo "🎉 INSTALASI SELESAI & SUKSES!"
echo "=========================================================="
echo "Dynamic Island sekarang aktif di bagian atas tengah layar Anda!"
echo ""
echo "Perintah cepat:"
echo "  • mint-island --settings : Membuka Menu Pengaturan"
echo "  • mint-island --status   : Memeriksa status aplikasi"
echo "  • ./uninstall.sh         : Menghapus instalasi"
echo "=========================================================="
