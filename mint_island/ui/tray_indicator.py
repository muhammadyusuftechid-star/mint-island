"""
System Tray StatusNotifierItem for Linux Mint Cinnamon
Provides tray icon in Cinnamon's bottom-right panel to control Mint-Island.
"""
import os
import dbus
import dbus.service
import logging
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class TrayIndicator(dbus.service.Object):
    def __init__(self, on_toggle_island_cb=None, on_open_settings_cb=None):
        self.on_toggle_island_cb = on_toggle_island_cb
        self.on_open_settings_cb = on_open_settings_cb
        self.is_registered = False

        try:
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SessionBus()
            self.service_name = f"org.kde.StatusNotifierItem-{os.getpid()}-1"
            self.bus_name = dbus.service.BusName(self.service_name, bus=self.bus)
            super().__init__(self.bus_name, "/StatusNotifierItem")
            self._register()
        except Exception as e:
            logging.error(f"Failed to initialize TrayIndicator: {e}")

    def _register(self):
        try:
            # Register with KDE / Cinnamon StatusNotifierWatcher
            watcher = self.bus.get_object('org.kde.StatusNotifierWatcher', '/StatusNotifierWatcher')
            watcher.RegisterStatusNotifierItem('/StatusNotifierItem', dbus_interface='org.kde.StatusNotifierWatcher')
            self.is_registered = True
            logging.info("TrayIndicator registered successfully on Cinnamon panel.")
        except Exception as e:
            logging.warning(f"StatusNotifierWatcher registration failed: {e}")

    # ==========================================
    # StatusNotifierItem D-Bus Methods
    # ==========================================
    @dbus.service.method('org.kde.StatusNotifierItem', in_signature='ii')
    def Activate(self, x, y):
        """Called when user left-clicks the tray icon in Cinnamon."""
        logging.info("Tray icon clicked (Activate). Opening settings window...")
        if self.on_open_settings_cb:
            GLib.idle_add(self.on_open_settings_cb)

    @dbus.service.method('org.kde.StatusNotifierItem', in_signature='ii')
    def ContextMenu(self, x, y):
        """Called when user right-clicks the tray icon."""
        logging.info("Tray icon right-clicked (ContextMenu). Opening settings...")
        if self.on_open_settings_cb:
            GLib.idle_add(self.on_open_settings_cb)

    @dbus.service.method('org.kde.StatusNotifierItem', in_signature='ii')
    def SecondaryActivate(self, x, y):
        """Called on middle-click to quickly toggle island visibility."""
        logging.info("Tray icon middle-clicked. Toggling island visibility...")
        if self.on_toggle_island_cb:
            GLib.idle_add(self.on_toggle_island_cb)

    # ==========================================
    # Properties Interface
    # ==========================================
    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        props = self.GetAll(interface)
        return props.get(prop, "")

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return {
            'Category': 'ApplicationStatus',
            'Id': 'mint-island',
            'Title': 'Mint-Island Controls',
            'Status': 'Active',
            'IconName': 'mint-island',
            'OverlayIconName': '',
            'AttentionIconName': '',
            'AttentionMovieName': '',
            'IconThemePath': '',
            'Menu': '/NO_DBUSMENU',
            'ItemIsMenu': False,
            'WindowId': 0
        }
