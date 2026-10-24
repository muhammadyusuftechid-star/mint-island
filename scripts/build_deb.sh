#!/usr/bin/env bash
# ==============================================================================
# Mint-Island: Native Debian (.deb) Package Builder
# Builds:
#   1. mint-island_1.0.0_all.deb   : Standard lightweight package (< 80 KB)
#   2. mint-island_1.0.0_amd64.deb : Compiled standalone ELF binary (optional)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

VERSION="1.0.0"
PKG_NAME="mint-island"
DIST_DIR="$SCRIPT_DIR/dist"
mkdir -p "$DIST_DIR"

echo "=========================================================="
echo "📦 Memulai Pembuatan Paket Debian (.deb) untuk $PKG_NAME v$VERSION..."
echo "=========================================================="

build_deb_package() {
    local ARCH="$1"          # "all" or "amd64"
    local IS_BINARY="$2"     # "true" or "false"
    local PKG_DEB="$DIST_DIR/${PKG_NAME}_${VERSION}_${ARCH}.deb"
    local BUILD_ROOT="$DIST_DIR/staging_${ARCH}"

    echo ""
    echo "----------------------------------------------------------"
    echo "🔨 Membangun paket Debian arsitektur: $ARCH (Binary: $IS_BINARY)..."
    echo "----------------------------------------------------------"

    rm -rf "$BUILD_ROOT" "$PKG_DEB"
    mkdir -p "$BUILD_ROOT/DEBIAN"
    mkdir -p "$BUILD_ROOT/usr/bin"
    mkdir -p "$BUILD_ROOT/usr/share/$PKG_NAME/mint_island/ui"
    mkdir -p "$BUILD_ROOT/usr/share/$PKG_NAME/mint_island/assets"
    mkdir -p "$BUILD_ROOT/usr/share/applications"
    mkdir -p "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps"
    mkdir -p "$BUILD_ROOT/usr/share/doc/$PKG_NAME"

    # Salin aset visual (CSS & SVG)
    cp mint_island/ui/styles.css "$BUILD_ROOT/usr/share/$PKG_NAME/mint_island/ui/"
    cp mint_island/assets/mint-island.svg "$BUILD_ROOT/usr/share/$PKG_NAME/mint_island/assets/"
    cp mint_island/assets/mint-island.svg "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps/mint-island.svg"

    if [ "$IS_BINARY" = "true" ]; then
        # Menggunakan Nuitka Compiled ELF Binary
        local COMPILED_BIN="$SCRIPT_DIR/build/nuitka/mint-island-bin"
        if [ ! -f "$COMPILED_BIN" ]; then
            echo "-> Biner Nuitka belum ada, menjalankan build_binary.sh..."
            bash "$SCRIPT_DIR/scripts/build_binary.sh"
            COMPILED_BIN="$SCRIPT_DIR/build/bin/mint-island"
        fi
        echo "-> Menyalin biner C/ELF ke /usr/bin/mint-island..."
        cp "$COMPILED_BIN" "$BUILD_ROOT/usr/bin/mint-island"
        chmod 755 "$BUILD_ROOT/usr/bin/mint-island"
    else
        # Menggunakan Standard Python Modules
        echo "-> Menyalin modul Python..."
        cp -r mint_island/* "$BUILD_ROOT/usr/share/$PKG_NAME/mint_island/"
        python3 -m compileall -q "$BUILD_ROOT/usr/share/$PKG_NAME"

        cat <<'EOF' > "$BUILD_ROOT/usr/bin/mint-island"
#!/usr/bin/env bash
exec /usr/bin/python3 /usr/share/mint-island/mint_island/main.py "$@"
EOF
        chmod 755 "$BUILD_ROOT/usr/bin/mint-island"
    fi

    # Buat Desktop Entry (Standar Industri: 1 Ikon + Desktop Actions)
    cat <<EOF > "$BUILD_ROOT/usr/share/applications/mint-island.desktop"
[Desktop Entry]
Type=Application
Name=Mint Island
GenericName=Dynamic Island HUD & Controls
Comment=Native Dynamic Island floating notch and control panel for Linux Mint
Exec=/usr/bin/mint-island --daemon
Icon=mint-island
Terminal=false
Categories=Utility;Settings;AudioVideo;
Keywords=island;dynamic;notch;music;volume;lirik;hud;mint;pulau;karaoke;settings;pengaturan;preferences;kontrol;
StartupNotify=true
Actions=Settings;

[Desktop Action Settings]
Name=Pengaturan Mint Island
Name[en]=Mint Island Settings
Exec=/usr/bin/mint-island --settings
EOF

    # Metadata Hak Cipta
    cat <<EOF > "$BUILD_ROOT/usr/share/doc/$PKG_NAME/copyright"
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: mint-island
Source: https://github.com/muhammadyusuftechid-star/mint-island

Files: *
Copyright: 2026 Muhammad Yusuf
License: GPL-3.0-or-later
EOF

    # Hitung Installed-Size
    local INSTALLED_SIZE
    INSTALLED_SIZE=$(du -sk "$BUILD_ROOT/usr" | awk '{print $1}')

    # DEBIAN/control
    cat <<EOF > "$BUILD_ROOT/DEBIAN/control"
Package: $PKG_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Maintainer: Muhammad Yusuf <https://github.com/muhammadyusuftechid-star>
Depends: python3 (>= 3.10), python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, python3-dbus, wmctrl, x11-utils
Recommends: playerctl, pipewire-pulse | pulseaudio-utils
Homepage: https://github.com/muhammadyusuftechid-star/mint-island
Description: Modern Native Dynamic Island for Linux Mint Cinnamon
 Mint-Island brings an elegant, lightweight Dynamic Island HUD to Linux Mint.
 Features include:
  * Hardware HUD popups for Volume, Brightness, and Battery Charging
  * Real-time synchronized karaoke lyrics powered by LRCLIB API
  * MPRIS Media Player integration (YouTube browser & Spotify)
  * Libadwaita Preferences Window Control Panel
  * Multi-monitor selector with dynamic hot-plugging
  * Native Cinnamon Tray Icon (StatusNotifierItem)
  * Extremely lightweight (<45 MB RAM and 0.0% CPU idle)
EOF

    # DEBIAN/postinst
    cat <<'EOF' > "$BUILD_ROOT/DEBIAN/postinst"
#!/bin/sh
set -e

case "$1" in
    configure)
        if which update-desktop-database >/dev/null 2>&1; then
            update-desktop-database -q /usr/share/applications || true
        fi
        if which gtk-update-icon-cache >/dev/null 2>&1; then
            gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
        fi
        if [ -n "$DISPLAY" ] && which dbus-send >/dev/null 2>&1; then
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
        fi
        ;;
esac
exit 0
EOF
    chmod 755 "$BUILD_ROOT/DEBIAN/postinst"

    # DEBIAN/prerm
    cat <<'EOF' > "$BUILD_ROOT/DEBIAN/prerm"
#!/bin/sh
set -e
case "$1" in
    remove|deconfigure|upgrade)
        pkill -f "/usr/bin/mint-island" 2>/dev/null || true
        pkill -f "/usr/share/mint-island" 2>/dev/null || true
        ;;
esac
exit 0
EOF
    chmod 755 "$BUILD_ROOT/DEBIAN/prerm"

    # DEBIAN/postrm
    cat <<'EOF' > "$BUILD_ROOT/DEBIAN/postrm"
#!/bin/sh
set -e
case "$1" in
    remove|purge)
        if which update-desktop-database >/dev/null 2>&1; then
            update-desktop-database -q /usr/share/applications || true
        fi
        if which gtk-update-icon-cache >/dev/null 2>&1; then
            gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
        fi
        ;;
esac
exit 0
EOF
    chmod 755 "$BUILD_ROOT/DEBIAN/postrm"

    # Bangun file .deb
    dpkg-deb --root-owner-group --build "$BUILD_ROOT" "$PKG_DEB"
    rm -rf "$BUILD_ROOT"

    echo "✔ Paket $ARCH selesai: $PKG_DEB ($(du -h "$PKG_DEB" | awk '{print $1}'))"
}

# 1. Bangun paket Universal Debian (.deb) - Sangat Cepat & Kompatibel Penuh
build_deb_package "all" "false"

# 2. Bangun paket Standalone Binary (amd64) jika diminta
if [ "$1" = "--with-binary" ] || [ -f "$SCRIPT_DIR/build/bin/mint-island" ]; then
    build_deb_package "amd64" "true"
fi

echo ""
echo "=========================================================="
echo "🎉 SEMUA PAKET DEBIAN BERHASIL DIBUAT DI FOLDER dist/!"
ls -lh "$DIST_DIR"/*.deb
echo "=========================================================="
