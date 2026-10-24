"""
Autostart Manager for Mint-Island
Manages ~/.config/autostart/mint-island.desktop for persistent launch across reboots.
"""
import sys
import os
import logging
from pathlib import Path

XDG_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
AUTOSTART_DIR = XDG_CONFIG / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "mint-island.desktop"

DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
Exec={exec_cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Mint Island
Comment=Dynamic Island HUD for Linux Mint Cinnamon
Icon=mint-island
Categories=Utility;TrayIcon;
StartupNotify=false
Terminal=false
"""

class AutostartManager:
    @staticmethod
    def is_enabled() -> bool:
        """Checks if autostart file exists and is active."""
        if not AUTOSTART_FILE.exists():
            return False
        try:
            with open(AUTOSTART_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            return "X-GNOME-Autostart-enabled=true" in content and "Hidden=false" in content
        except Exception as e:
            logging.error(f"Error checking autostart file: {e}")
            return False

    @staticmethod
    def enable() -> bool:
        """Creates or updates the autostart .desktop entry."""
        try:
            AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
            local_bin = Path.home() / ".local" / "bin" / "mint-island"
            if local_bin.exists() and os.access(local_bin, os.X_OK):
                exec_cmd = f'"{local_bin}" --daemon'
            else:
                python_exec = sys.executable
                main_py_path = Path(__file__).resolve().parent / "main.py"
                exec_cmd = f'{python_exec} "{main_py_path}" --daemon'

            content = DESKTOP_TEMPLATE.format(
                exec_cmd=exec_cmd
            )

            with open(AUTOSTART_FILE, "w", encoding="utf-8") as f:
                f.write(content)

            # Ensure readable/executable permissions
            AUTOSTART_FILE.chmod(0o755)
            logging.info(f"Autostart enabled at {AUTOSTART_FILE}")
            return True
        except Exception as e:
            logging.error(f"Failed to enable autostart: {e}")
            return False

    @staticmethod
    def disable() -> bool:
        """Removes the autostart .desktop entry."""
        try:
            if AUTOSTART_FILE.exists():
                AUTOSTART_FILE.unlink()
                logging.info(f"Autostart removed at {AUTOSTART_FILE}")
            return True
        except Exception as e:
            logging.error(f"Failed to disable autostart: {e}")
            return False
