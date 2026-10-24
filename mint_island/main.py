#!/usr/bin/env python3
"""
Mint-Island: Dynamic Island Entry Point
Includes Settings Window & System Tray StatusNotifierItem
"""
import sys
import os
import signal
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from mint_island.config import config_manager
from mint_island.autostart import AutostartManager
from mint_island.license import license_manager
from mint_island.ui.island_window import IslandWindow
from mint_island.ui.settings_window import SettingsWindow
from mint_island.ui.tray_indicator import TrayIndicator

class MintIslandApplication(Adw.Application):
    def __init__(self, test_mode=False, open_settings_on_start=False):
        super().__init__(
            application_id="org.linuxmint.dynamicisland",
            flags=0
        )
        self.test_mode = test_mode
        self.open_settings_on_start = open_settings_on_start
        self.island_window = None
        self.settings_window = None
        self.tray = None

    def do_activate(self):
        """Called when application is activated."""
        # If application is already running in background, re-activating from menu opens Settings
        if self.island_window is not None:
            logging.info("Mint-Island re-activated from menu: presenting Settings window.")
            self.open_settings()
            return

        # Ensure autostart state matches config
        if config_manager.get("general", "autostart_on_boot", True):
            if not AutostartManager.is_enabled():
                AutostartManager.enable()

        # Hold application in background to prevent daemon exit when windows are hidden
        if not self.test_mode:
            self.hold()

        # Initialize Main Island Window
        self.island_window = IslandWindow(self)

        is_enabled = config_manager.get("general", "enabled", True)
        if is_enabled or self.test_mode:
            self.island_window.present()
            logging.info("Mint-Island window presented.")
        else:
            self.island_window.set_visible(False)
            logging.info("Mint-Island started in hidden/disabled state.")

        # Initialize System Tray
        if not self.tray and not self.test_mode:
            try:
                self.tray = TrayIndicator(
                    on_toggle_island_cb=self.toggle_island,
                    on_open_settings_cb=self.open_settings
                )
            except Exception as e:
                logging.warning(f"Could not initialize system tray: {e}")

        # If user launched with --settings flag
        if self.open_settings_on_start:
            self.open_settings()

        if self.test_mode:
            logging.info("Running in test mode. Exiting in 3 seconds...")
            GLib.timeout_add(3000, self.quit)

    def open_settings(self):
        """Opens or presents the Control Panel / Preferences window."""
        try:
            if not self.settings_window:
                self.settings_window = SettingsWindow(
                    app=self,
                    on_config_changed_cb=self.on_config_changed
                )
            self.settings_window.present()
        except Exception:
            self.settings_window = SettingsWindow(
                app=self,
                on_config_changed_cb=self.on_config_changed
            )
            self.settings_window.present()

    def toggle_island(self):
        """Toggles the visibility of the Dynamic Island."""
        if self.island_window:
            current_visible = self.island_window.get_visible()
            new_state = not current_visible
            self.island_window.set_visible(new_state)
            config_manager.set("general", "enabled", new_state)
            logging.info(f"Dynamic Island visibility toggled to: {new_state}")

    def on_config_changed(self, key, value):
        """Handles live configuration updates without restarting the application."""
        logging.info(f"Config updated in GUI: {key} = {value}")
        if not self.island_window:
            return

        if key == "enabled":
            self.island_window.set_visible(value)
        else:
            self.island_window.on_config_updated(key, value)


def main():
    parser = argparse.ArgumentParser(description="Mint-Island: Native Dynamic Island for Linux Mint")
    parser.add_argument("--daemon", action="store_true", help="Run Mint-Island in background daemon mode")
    parser.add_argument("--settings", action="store_true", help="Open Mint-Island Control Panel GUI")
    parser.add_argument("--test", action="store_true", help="Run self-diagnostic test and exit")
    parser.add_argument("--autostart-enable", action="store_true", help="Enable launch on laptop reboot")
    parser.add_argument("--autostart-disable", action="store_true", help="Disable launch on laptop reboot")
    parser.add_argument("--status", action="store_true", help="Check status of Mint-Island and autostart")
    parser.add_argument("--license", action="store_true", help="Display current Pro license status")
    parser.add_argument("--activate", type=str, metavar="KEY", help="Activate Pro license key")
    parser.add_argument("--deactivate", action="store_true", help="Deactivate Pro license")

    args = parser.parse_args()

    if args.activate:
        print(f"⏳ Verifying and activating key: {args.activate}...")
        success, msg = license_manager.activate(args.activate)
        if success:
            print(f"✅ {msg}")
        else:
            print(f"❌ {msg}")
        return

    if args.deactivate:
        if license_manager.deactivate():
            print("ℹ️ License deactivated successfully.")
        else:
            print("❌ Failed to deactivate license.")
        return

    if args.license:
        info = license_manager.get_info()
        print("=== Mint-Island License Info ===")
        print(f"Pro Active : {info.get('is_pro', False)}")
        print(f"Tier       : {info.get('tier', 'Free')}")
        print(f"Key        : {info.get('masked_key') or '(None)'}")
        print(f"Activated  : {info.get('activated_at') or '(Not activated)'}")
        return

    if args.autostart_enable:
        success = AutostartManager.enable()
        config_manager.set("general", "autostart_on_boot", True)
        print("✅ Autostart enabled successfully." if success else "❌ Failed to enable autostart.")
        return

    if args.autostart_disable:
        success = AutostartManager.disable()
        config_manager.set("general", "autostart_on_boot", False)
        print("✅ Autostart disabled successfully." if success else "❌ Failed to disable autostart.")
        return

    if args.status:
        config = config_manager.load()
        autostart_active = AutostartManager.is_enabled()
        lic_info = license_manager.get_info()
        print("=== Mint-Island Status ===")
        print(f"Enabled in config: {config.get('general', {}).get('enabled', False)}")
        print(f"Autostart enabled: {autostart_active}")
        print(f"Pro License      : {'Active 🌟' if lic_info.get('is_pro') else 'Free Edition'}")
        from mint_island.config import CONFIG_FILE
        from mint_island.autostart import AUTOSTART_FILE
        print(f"Config path      : {CONFIG_FILE}")
        print(f"Autostart path   : {AUTOSTART_FILE}")
        return

    # Handle graceful exit on Ctrl+C / SIGINT
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = MintIslandApplication(
        test_mode=args.test,
        open_settings_on_start=args.settings
    )
    app.run([])

if __name__ == "__main__":
    main()
