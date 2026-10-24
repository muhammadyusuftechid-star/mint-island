#!/usr/bin/env bash
# ==============================================================================
# Mint-Island: Uninstaller Script
# ==============================================================================
set -e

echo "Menghapus instalasi Mint-Island..."

# 1. Hentikan proses yang berjalan
pkill -f "mint_island/main.py" 2>/dev/null || true

# 2. Hapus file desktop & pintasan
rm -f "$HOME/.local/bin/mint-island"
rm -f "$HOME/.local/share/applications/mint-island.desktop"
rm -f "$HOME/.local/share/applications/mint-island-settings.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/mint-island.svg"
rm -f "$HOME/.config/autostart/mint-island.desktop"

# 3. Refresh database desktop
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo "✔ Mint-Island telah berhasil dicopot dari sistem Anda."
