"""
Power Profile Monitor via net.hadess.PowerProfiles D-Bus
Allows switching between power-saver, balanced, and performance profiles.
"""
import dbus
import logging
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class PowerProfileMonitor:
    def __init__(self, on_profile_changed_cb=None):
        self.on_profile_changed_cb = on_profile_changed_cb
        self.active_profile = "balanced"
        self.available_profiles = ["power-saver", "balanced", "performance"]
        self.props_iface = None
        self._setup()

    def _setup(self):
        try:
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            pp_obj = bus.get_object('net.hadess.PowerProfiles', '/net/hadess/PowerProfiles')
            self.props_iface = dbus.Interface(pp_obj, 'org.freedesktop.DBus.Properties')

            # Initial state
            self.active_profile = str(self.props_iface.Get('net.hadess.PowerProfiles', 'ActiveProfile'))
            raw_profiles = self.props_iface.Get('net.hadess.PowerProfiles', 'Profiles')
            self.available_profiles = [str(p['Profile']) for p in raw_profiles]

            # Listen for profile changes from system or other apps
            bus.add_signal_receiver(
                self._on_properties_changed,
                signal_name='PropertiesChanged',
                dbus_interface='org.freedesktop.DBus.Properties',
                path='/net/hadess/PowerProfiles'
            )
            logging.info(f"PowerProfileMonitor initialized: ActiveProfile={self.active_profile}")
        except Exception as e:
            logging.warning(f"PowerProfileMonitor unavailable: {e}")

    def _on_properties_changed(self, interface, changed_props, invalidated_props):
        if 'ActiveProfile' in changed_props:
            new_profile = str(changed_props['ActiveProfile'])
            if new_profile != self.active_profile:
                self.active_profile = new_profile
                logging.info(f"Power profile changed: {self.active_profile}")
                if self.on_profile_changed_cb:
                    GLib.idle_add(self.on_profile_changed_cb, self.active_profile)

    def set_profile(self, profile_name: str) -> bool:
        """Changes the active power profile."""
        if profile_name not in self.available_profiles:
            logging.warning(f"Profile {profile_name} not in available: {self.available_profiles}")
            return False

        if not self.props_iface:
            return False

        try:
            self.props_iface.Set(
                'net.hadess.PowerProfiles',
                'ActiveProfile',
                dbus.String(profile_name, variant_level=1)
            )
            self.active_profile = profile_name
            if self.on_profile_changed_cb:
                GLib.idle_add(self.on_profile_changed_cb, self.active_profile)
            return True
        except Exception as e:
            logging.error(f"Failed to set power profile to {profile_name}: {e}")
            return False
