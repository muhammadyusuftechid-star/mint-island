"""
Bluetooth & TWS Headphone Monitor for Mint-Island
Interacts with org.bluez on D-Bus SystemBus to detect device connection/disconnection
and battery percentage levels (e.g. TWS earbuds, headphones, wireless keyboards).
"""
import dbus
import logging
from typing import Optional, List, Dict
from gi.repository import GLib

def resolve_device_emoji(name: str, icon: str = "") -> str:
    """Returns an intuitive emoji according to BlueZ icon and device name."""
    name_lower = name.lower()
    icon_lower = icon.lower()

    if any(k in icon_lower for k in ("headset", "headphone", "audio")) or \
       any(k in name_lower for k in ("r50i", "ear", "bud", "tws", "airpod", "headphone", "headset", "soundcore", "soundpeats")):
        return "🎧"
    if "speaker" in icon_lower or "speaker" in name_lower or "soundbar" in name_lower:
        return "🔊"
    if "keyboard" in icon_lower or "keyboard" in name_lower:
        return "⌨️"
    if any(k in icon_lower for k in ("mouse", "pointing")):
        return "🖱️"
    if any(k in icon_lower for k in ("game", "gamepad", "joystick")):
        return "🎮"
    return "📶"

class BluetoothMonitor:
    def __init__(self, on_device_event_cb=None):
        self.on_device_event_cb = on_device_event_cb
        self.bus = None
        self._last_event_cache = {}  # (path, is_connected) -> timestamp to avoid double triggers
        self._setup()

    def _setup(self):
        try:
            from dbus.mainloop.glib import DBusGMainLoop
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()

            # Listen for property changes (Connected, Battery Percentage)
            self.bus.add_signal_receiver(
                self._on_properties_changed,
                signal_name="PropertiesChanged",
                dbus_interface="org.freedesktop.DBus.Properties",
                path_keyword="path"
            )

            # Listen for new interfaces added dynamically (e.g. Battery1 appearing after connection)
            self.bus.add_signal_receiver(
                self._on_interfaces_added,
                signal_name="InterfacesAdded",
                dbus_interface="org.freedesktop.DBus.ObjectManager"
            )

            logging.info("BluetoothMonitor initialized: listening to BlueZ signals on SystemBus.")
        except Exception as e:
            logging.warning(f"BluetoothMonitor could not connect to BlueZ: {e}")
            self.bus = None

    def get_connected_devices(self) -> List[Dict]:
        """Returns list of currently connected Bluetooth devices with name, emoji, and battery."""
        if not self.bus:
            return []

        devices = []
        try:
            obj = self.bus.get_object("org.bluez", "/")
            mgr = dbus.Interface(obj, "org.freedesktop.DBus.ObjectManager")
            objects = mgr.GetManagedObjects()

            for path, ifaces in objects.items():
                if "org.bluez.Device1" in ifaces:
                    dev = ifaces["org.bluez.Device1"]
                    if dev.get("Connected", False):
                        name = str(dev.get("Alias", dev.get("Name", "Bluetooth Device")))
                        icon = str(dev.get("Icon", ""))
                        emoji = resolve_device_emoji(name, icon)
                        battery = None
                        if "org.bluez.Battery1" in ifaces:
                            battery = int(ifaces["org.bluez.Battery1"].get("Percentage", 0))
                        devices.append({
                            "path": str(path),
                            "name": name,
                            "emoji": emoji,
                            "battery": battery
                        })
        except Exception as e:
            logging.warning(f"Error querying connected Bluetooth devices: {e}")
        return devices

    def _query_device(self, path: str) -> Optional[Dict]:
        """Queries single device properties by object path."""
        if not self.bus:
            return None
        try:
            dev_obj = self.bus.get_object("org.bluez", path)
            dev_props = dbus.Interface(dev_obj, "org.freedesktop.DBus.Properties")

            name = str(dev_props.Get("org.bluez.Device1", "Alias"))
            icon = ""
            try:
                icon = str(dev_props.Get("org.bluez.Device1", "Icon"))
            except Exception:
                pass

            connected = bool(dev_props.Get("org.bluez.Device1", "Connected"))
            emoji = resolve_device_emoji(name, icon)

            battery = None
            try:
                battery = int(dev_props.Get("org.bluez.Battery1", "Percentage"))
            except Exception:
                pass

            return {
                "path": path,
                "name": name,
                "emoji": emoji,
                "connected": connected,
                "battery": battery
            }
        except Exception as e:
            logging.debug(f"Could not query BlueZ device at {path}: {e}")
            return None

    def _on_properties_changed(self, interface, changed, invalidated, path=None):
        """Handler for BlueZ property updates."""
        try:
            if not path:
                return
            if interface == "org.bluez.Device1" and "Connected" in changed:
                is_connected = bool(changed["Connected"])
                self._handle_connection_change(str(path), is_connected)
            elif interface == "org.bluez.Battery1" and "Percentage" in changed:
                battery = int(changed["Percentage"])
                self._handle_battery_change(str(path), battery)
        except Exception as e:
            logging.error(f"Error in Bluetooth properties change handler: {e}")

    def _on_interfaces_added(self, path, interfaces):
        """Handler when new interfaces like org.bluez.Battery1 appear dynamically."""
        try:
            if "org.bluez.Battery1" in interfaces:
                battery = int(interfaces["org.bluez.Battery1"].get("Percentage", 0))
                self._handle_battery_change(str(path), battery)
        except Exception as e:
            logging.error(f"Error in Bluetooth interfaces added handler: {e}")

    def _handle_connection_change(self, path: str, is_connected: bool):
        info = self._query_device(path)
        if not info:
            return

        name = info["name"]
        emoji = info["emoji"]
        battery = info["battery"]

        # If connected and battery not yet ready, schedule a quick retry in 600ms
        if is_connected and battery is None:
            GLib.timeout_add(600, self._retry_battery_query, path, name, emoji)

        logging.info(f"Bluetooth device event: {name} (Connected={is_connected}, Battery={battery}%, Icon={emoji})")
        if self.on_device_event_cb:
            GLib.idle_add(self.on_device_event_cb, name, is_connected, battery, emoji, path)

    def _retry_battery_query(self, path: str, name: str, emoji: str):
        info = self._query_device(path)
        if info and info.get("connected") and info.get("battery") is not None:
            battery = info["battery"]
            logging.info(f"Bluetooth battery resolved on retry: {name} ({battery}%)")
            if self.on_device_event_cb:
                GLib.idle_add(self.on_device_event_cb, name, True, battery, emoji, path)
        return False

    def _handle_battery_change(self, path: str, battery: int):
        info = self._query_device(path)
        if info and info.get("connected"):
            name = info["name"]
            emoji = info["emoji"]
            logging.info(f"Bluetooth battery updated: {name} ({battery}%)")
            if self.on_device_event_cb:
                GLib.idle_add(self.on_device_event_cb, name, True, battery, emoji, path)
