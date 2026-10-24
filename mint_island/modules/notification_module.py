"""
Desktop Notification Interceptor for Mint-Island
Eavesdrops on org.freedesktop.Notifications via D-Bus to display notifications in the island.
"""
import dbus
import logging
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

def get_app_emoji(app_name: str, summary: str) -> str:
    """Returns an intuitive emoji based on app name or summary."""
    text = f"{app_name} {summary}".lower()
    if any(k in text for k in ("telegram", "whatsapp", "chat", "discord", "slack", "signal", "message", "sms", "pesan")):
        return "💬"
    if any(k in text for k in ("brave", "chrome", "firefox", "download", "wget", "curl", "unduhan")):
        return "📥"
    if any(k in text for k in ("mail", "thunderbird", "evolution", "gmail", "outlook", "email", "surat")):
        return "📧"
    if any(k in text for k in ("spotify", "music", "rhythmbox", "vlc", "mpv", "audacious", "lagu")):
        return "🎵"
    if any(k in text for k in ("terminal", "bash", "alacritty", "kitty", "konsole", "update", "pembaruan")):
        return "💻"
    if any(k in text for k in ("battery", "power", "charger", "baterai", "daya")):
        return "⚡"
    if any(k in text for k in ("bluetooth", "headphone", "tws", "audio", "headset")):
        return "🎧"
    if any(k in text for k in ("calendar", "kalender", "reminder", "pengingat", "jadwal", "alarm")):
        return "📅"
    if any(k in text for k in ("error", "warning", "fail", "gagal", "peringatan", "alert")):
        return "⚠️"
    return "🔔"

class NotificationMonitor:
    def __init__(self, on_notification_cb=None):
        self.on_notification_cb = on_notification_cb
        self.bus = None
        self._setup()

    def _setup(self):
        try:
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SessionBus()
            self.bus.add_match_string(
                "eavesdrop=true,type='method_call',interface='org.freedesktop.Notifications',member='Notify'"
            )
            self.bus.add_message_filter(self._on_message)
            logging.info("NotificationMonitor initialized: eavesdropping on org.freedesktop.Notifications.")
        except Exception as e:
            logging.warning(f"Could not initialize NotificationMonitor: {e}")

    def _on_message(self, bus, message):
        try:
            if message.get_interface() == 'org.freedesktop.Notifications' and message.get_member() == 'Notify':
                args = message.get_args_list()
                if len(args) >= 5:
                    app_name = str(args[0]).strip()
                    app_icon = str(args[2]).strip()
                    summary = str(args[3]).strip()
                    body = str(args[4]).strip()

                    # Ignore self or internal daemon notifications
                    if app_name.lower() in ("mint-island", "mint_island"):
                        return

                    if not summary and not body:
                        return

                    emoji = get_app_emoji(app_name, summary)
                    logging.info(f"Captured desktop notification: [{app_name}] {summary} - {body}")
                    if self.on_notification_cb:
                        GLib.idle_add(self.on_notification_cb, app_name, summary, body, app_icon, emoji)
        except Exception as e:
            logging.error(f"Error handling notification D-Bus message: {e}")
