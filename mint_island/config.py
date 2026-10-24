"""
Config Manager for Mint-Island
Manages configuration file at ~/.config/dynamic-island/config.json
"""
import os
import copy
import json
import logging
from pathlib import Path

# Dynamic XDG Config Directory
XDG_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
CONFIG_DIR = XDG_CONFIG / "mint-island"
CONFIG_FILE = CONFIG_DIR / "config.json"
LEGACY_CONFIG_FILE = Path.home() / ".config" / "dynamic-island" / "config.json"

DEFAULT_CONFIG = {
    "general": {
        "enabled": True,
        "autostart_on_boot": True,
        "start_minimized": False
    },
    "modules": {
        "media_player": True,
        "show_synced_lyrics": True,
        "battery_charging": True,
        "power_profile_switcher": True,
        "show_battery_estimate": True,
        "volume_hud": True,
        "brightness_hud": True,
        "system_notifications": True,
        "bluetooth_hud": True,
        "caps_lock_hud": True
    },
    "appearance": {
        "position": "top-center",
        "monitor_index": 0,
        "y_offset": 8,
        "scale_percent": 100,
        "theme": "glass-dark",
        "hud_timeout_seconds": 3.0,
        "enable_animations": True,
        "compact_micro_pill": True
    }
}

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load()

    def load(self) -> dict:
        """Loads configuration from file or initializes defaults if not present."""
        try:
            if not CONFIG_DIR.exists():
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                self.config = self._deep_merge(DEFAULT_CONFIG, user_config)
            elif LEGACY_CONFIG_FILE.exists():
                with open(LEGACY_CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                self.config = self._deep_merge(DEFAULT_CONFIG, user_config)
                self.save()  # migrate to new XDG location
            else:
                self.config = copy.deepcopy(DEFAULT_CONFIG)
                self.save()
        except Exception as e:
            logging.error(f"Error loading config.json: {e}. Using defaults.")
            self.config = copy.deepcopy(DEFAULT_CONFIG)
            self.save()

        return self.config

    def save(self) -> bool:
        """Saves current configuration to file."""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving config.json: {e}")
            return False

    def get(self, section: str, key: str, default=None):
        """Retrieve a specific setting."""
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value) -> bool:
        """Update a setting and persist to disk."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        return self.save()

    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = copy.deepcopy(base)
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result

# Global singleton
config_manager = ConfigManager()
