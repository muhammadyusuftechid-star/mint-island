"""
Display Brightness Listener via Cinnamon Settings Daemon & sysfs
Monitors brightness Fn key changes without CPU polling.
"""
import glob
import dbus
import logging
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class BrightnessMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.current_brightness = 50
        self._setup()

    def _setup(self):
        try:
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            obj = bus.get_object('org.cinnamon.SettingsDaemon.Power', '/org/cinnamon/SettingsDaemon/Power')
            self.screen_iface = dbus.Interface(obj, 'org.cinnamon.SettingsDaemon.Power.Screen')

            # Initial value
            self.current_brightness = int(self.screen_iface.GetPercentage())

            # Connect to Changed signal
            self.screen_iface.connect_to_signal('Changed', self._on_brightness_changed)
            logging.info(f"BrightnessMonitor initialized: {self.current_brightness}%")
        except Exception as e:
            logging.warning(f"Cinnamon Brightness D-Bus setup failed ({e}), falling back to sysfs")
            self._setup_sysfs_fallback()

    def _setup_sysfs_fallback(self):
        try:
            paths = glob.glob('/sys/class/backlight/*/actual_brightness')
            max_paths = glob.glob('/sys/class/backlight/*/max_brightness')
            if paths and max_paths:
                with open(paths[0]) as f:
                    curr = int(f.read().strip())
                with open(max_paths[0]) as f:
                    max_b = int(f.read().strip())
                self.current_brightness = int((curr / max_b) * 100)
                logging.info(f"Sysfs Brightness initialized: {self.current_brightness}%")
        except Exception as err:
            logging.error(f"Sysfs brightness read failed: {err}")

    def _on_brightness_changed(self, *args, **kwargs):
        try:
            if hasattr(self, 'screen_iface') and self.screen_iface:
                new_val = int(self.screen_iface.GetPercentage())
            else:
                new_val = self._read_sysfs_percentage()

            if new_val is not None and new_val != self.current_brightness:
                self.current_brightness = new_val
                GLib.idle_add(self.callback, self.current_brightness)
        except Exception as e:
            logging.debug(f"Error reading brightness on signal: {e}")
            sysfs_val = self._read_sysfs_percentage()
            if sysfs_val is not None and sysfs_val != self.current_brightness:
                self.current_brightness = sysfs_val
                GLib.idle_add(self.callback, self.current_brightness)

    def _read_sysfs_percentage(self):
        try:
            paths = glob.glob('/sys/class/backlight/*/actual_brightness')
            max_paths = glob.glob('/sys/class/backlight/*/max_brightness')
            if paths and max_paths:
                with open(paths[0]) as f:
                    curr = int(f.read().strip())
                with open(max_paths[0]) as f:
                    max_b = int(f.read().strip())
                return int((curr / max_b) * 100)
        except Exception:
            pass
        return None

    def set_brightness(self, brightness: int):
        """Sets display brightness percentage (1-100%)."""
        val = max(1, min(100, int(brightness)))
        self.current_brightness = val
        if hasattr(self, 'screen_iface') and self.screen_iface:
            try:
                self.screen_iface.SetPercentage(dbus.UInt32(val))
                return
            except Exception as e:
                logging.debug(f"Error setting brightness via Cinnamon D-Bus: {e}")

        # Fallback to sysfs if writable
        try:
            max_paths = glob.glob('/sys/class/backlight/*/max_brightness')
            curr_paths = glob.glob('/sys/class/backlight/*/brightness')
            if max_paths and curr_paths:
                with open(max_paths[0]) as f:
                    max_b = int(f.read().strip())
                target_val = int((val / 100.0) * max_b)
                with open(curr_paths[0], 'w') as f:
                    f.write(str(target_val))
        except Exception:
            pass

