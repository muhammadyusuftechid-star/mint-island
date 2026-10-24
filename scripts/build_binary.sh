#!/usr/bin/env bash
# ==============================================================================
# Mint-Island: Commercial Native ELF Binary Compiler (Nuitka + GCC)
# Compiles Python codebase into standalone, reverse-engineering resistant ELF binary.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

OUTPUT_DIR="$SCRIPT_DIR/build/bin"
OUTPUT_BIN="mint-island"
VENV_DIR="$SCRIPT_DIR/.build_venv"

echo "=========================================================="
echo "⚡ Mengompilasi Mint-Island ke Mesin Biner Native (ELF)..."
echo "=========================================================="

# 1. Pastikan build virtualenv dan nuitka tersedia
if [ ! -f "$VENV_DIR/bin/nuitka" ]; then
    echo "-> Menyiapkan lingkungan kompilasi Python..."
    python3 -m venv "$VENV_DIR" --system-site-packages
    "$VENV_DIR/bin/pip" install nuitka
fi

mkdir -p "$OUTPUT_DIR"

# 2. Kompilasi menggunakan Nuitka dengan GCC backend
echo "-> Menjalankan kompilasi Nuitka C..."
"$VENV_DIR/bin/nuitka" \
    --follow-imports \
    --include-package=mint_island \
    --output-dir="$OUTPUT_DIR" \
    --output-filename="$OUTPUT_BIN" \
    --remove-output \
    mint_island/main.py

echo "=========================================================="
echo "🎉 KOMPILASI MESIN BINER SELESAI!"
echo "Lokasi Biner: $OUTPUT_DIR/$OUTPUT_BIN"
echo "Ukuran File : $(du -h "$OUTPUT_DIR/$OUTPUT_BIN" | awk '{print $1}')"
echo "Tipe Format : $(file "$OUTPUT_DIR/$OUTPUT_BIN" | awk -F': ' '{print $2}')"
echo "=========================================================="
