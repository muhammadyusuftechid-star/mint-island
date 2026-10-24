"""
Battery & Charger Listener via UPower D-Bus
Monitors charger plug/unplug events and battery levels without busy loops.
"""
import dbus
import logging
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from mint_island.i18n import _

class BatteryMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.is_charging = False
        self.percentage = 100
        self.time_to_empty = 0
        self.time_to_full = 0
        self.capacity = 100.0
        self.device_path = None
        self.props_iface = None
        self._setup()

    def _setup(self):
        try:
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            self.upower_obj = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
            upower = dbus.Interface(self.upower_obj, 'org.freedesktop.UPower')
            self.device_path = str(upower.GetDisplayDevice())

            dev_obj = bus.get_object('org.freedesktop.UPower', self.device_path)
            self.props_iface = dbus.Interface(dev_obj, 'org.freedesktop.DBus.Properties')

            # Initial state
            props = self.props_iface.GetAll('org.freedesktop.UPower.Device')
            state = int(props.get('State', 2))
            self.percentage = int(props.get('Percentage', 100))
            self.time_to_empty = int(props.get('TimeToEmpty', 0))
            self.time_to_full = int(props.get('TimeToFull', 0))
            self.capacity = float(props.get('Capacity', 100.0))
            # State: 1 = Charging, 4 = Fully Charged, 5 = Pending Charge, or AC connected
            self.is_charging = (state in (1, 4, 5)) or (not on_battery)

            # Listen for property changes
            bus.add_signal_receiver(
                self._on_properties_changed,
                signal_name='PropertiesChanged',
                dbus_interface='org.freedesktop.DBus.Properties',
                path=self.device_path
            )
            # Also listen to UPower daemon changes (like AC plug/unplug)
            bus.add_signal_receiver(
                self._on_upower_changed,
                signal_name='PropertiesChanged',
                dbus_interface='org.freedesktop.DBus.Properties',
                path='/org/freedesktop/UPower'
            )
            logging.info(f"BatteryMonitor initialized: {self.percentage}% (Charging={self.is_charging})")
        except Exception as e:
            logging.error(f"Failed to initialize BatteryMonitor: {e}")

    def _check_on_battery(self) -> bool:
        try:
            if hasattr(self, 'upower_obj') and self.upower_obj:
                return bool(self.upower_obj.Get('org.freedesktop.UPower', 'OnBattery', dbus_interface='org.freedesktop.DBus.Properties'))
        except Exception:
            pass
        return True

    def _on_upower_changed(self, interface, changed_props, invalidated_props):
        if 'OnBattery' in changed_props:
            on_battery = bool(changed_props['OnBattery'])
            new_charging = not on_battery
            if new_charging != self.is_charging:
                self.is_charging = new_charging
                is_low = (self.percentage <= 15 and not self.is_charging)
                GLib.idle_add(self.callback, self.is_charging, self.percentage, is_low, True)

    def _on_properties_changed(self, interface, changed_props, invalidated_props):
        if 'TimeToEmpty' in changed_props:
            self.time_to_empty = int(changed_props['TimeToEmpty'])
        if 'TimeToFull' in changed_props:
            self.time_to_full = int(changed_props['TimeToFull'])
        if 'Capacity' in changed_props:
            self.capacity = float(changed_props['Capacity'])

        if 'State' in changed_props or 'Percentage' in changed_props:
            new_state = int(changed_props.get('State', 1 if self.is_charging else 2))
            on_battery = self._check_on_battery()
            new_charging = (new_state in (1, 4, 5)) or (not on_battery)
            new_percentage = int(changed_props.get('Percentage', self.percentage))

            state_changed = (new_charging != self.is_charging)
            pct_changed = (abs(new_percentage - self.percentage) >= 1)

            self.is_charging = new_charging
            self.percentage = new_percentage

            if state_changed or pct_changed:
                is_low = (self.percentage <= 15 and not self.is_charging)
                # Dispatch to GTK main thread
                GLib.idle_add(
                    self.callback,
                    self.is_charging,
                    self.percentage,
                    is_low,
                    state_changed
                )

    def get_estimate_str(self) -> str:
        """Returns human-readable battery estimate or health string."""
        parts = []
        h_suffix = "h" if _("Full in") == "Full in" else "j"
        m_suffix = "m"
        if self.is_charging:
            if self.percentage >= 99:
                parts.append(_("Fully Charged"))
            elif self.time_to_full > 0:
                hours = self.time_to_full // 3600
                mins = (self.time_to_full % 3600) // 60
                if hours > 0:
                    parts.append(f"{_('Full in')} {hours}{h_suffix} {mins}{m_suffix}")
                else:
                    parts.append(f"{_('Full in')} {mins}{m_suffix}")
            else:
                parts.append(_("Charging (AC)"))
        else:
            if self.time_to_empty > 0:
                hours = self.time_to_empty // 3600
                mins = (self.time_to_empty % 3600) // 60
                if hours > 0:
                    parts.append(f"{_('Remaining')} {hours}{h_suffix} {mins}{m_suffix}")
                else:
                    parts.append(f"{_('Remaining')} {mins}{m_suffix}")
            else:
                parts.append(_("Battery Power"))

        if self.capacity > 0 and self.capacity < 100:
            parts.append(f"{_('Health')} {int(round(self.capacity))}%")

        return " • ".join(parts)
