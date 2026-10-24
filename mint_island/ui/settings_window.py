"""
Control Panel & Settings GUI for Mint-Island
Built with Libadwaita (Adw.PreferencesWindow) matching Linux Mint aesthetics.
Includes Multi-Page navigation: Preferences & Pro License Activation.
"""
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk, Gio

from mint_island.config import config_manager
from mint_island.autostart import AutostartManager
from mint_island.license import license_manager
from mint_island.i18n import _, i18n

class SettingsWindow(Adw.PreferencesWindow):
    def __init__(self, app, on_config_changed_cb=None):
        super().__init__(application=app)
        self.set_title(_("Mint-Island Settings"))
        self.set_default_size(540, 650)
        self.add_css_class("settings-window")
        self.on_config_changed_cb = on_config_changed_cb

        # Hide on close rather than destroying
        self.connect("close-request", self._on_close_request)

        self._build_ui()

    def _on_close_request(self, *args):
        self.set_visible(False)
        return True

    def _build_ui(self):
        # ==========================================
        # PAGE 1: Pengaturan Umum & Modul (Preferences)
        # ==========================================
        page_general = Adw.PreferencesPage()
        page_general.set_title(_("Settings"))
        page_general.set_icon_name("preferences-system-symbolic")

        # ------------------------------------------
        # Grup 1: Status Utama (General)
        # ------------------------------------------
        group_general = Adw.PreferencesGroup()
        group_general.set_title(_("Main Status"))
        group_general.set_description(_("Master controls for island and system autostart."))

        # Master Switch: Enabled
        row_enabled = Adw.ActionRow()
        row_enabled.set_title(_("Enable Dynamic Island"))
        row_enabled.set_subtitle(_("Show floating island at top of screen"))
        self.sw_enabled = Gtk.Switch()
        self.sw_enabled.set_valign(Gtk.Align.CENTER)
        self.sw_enabled.set_active(config_manager.get("general", "enabled", True))
        self.sw_enabled.connect("state-set", self._on_enabled_toggled)
        row_enabled.add_suffix(self.sw_enabled)
        group_general.add(row_enabled)

        # Autostart Switch
        row_autostart = Adw.ActionRow()
        row_autostart.set_title(_("Start Automatically on Boot"))
        row_autostart.set_subtitle(_("Launch on user login without terminal"))
        self.sw_autostart = Gtk.Switch()
        self.sw_autostart.set_valign(Gtk.Align.CENTER)
        self.sw_autostart.set_active(AutostartManager.is_enabled())
        self.sw_autostart.connect("state-set", self._on_autostart_toggled)
        row_autostart.add_suffix(self.sw_autostart)
        group_general.add(row_autostart)

        # Interface Language Selector
        row_lang = Adw.ComboRow()
        row_lang.set_title(_("Interface Language"))
        row_lang.set_subtitle(_("Select display language for island and controls"))
        lang_model = Gtk.StringList.new(["Bahasa Indonesia", "English (US)"])
        row_lang.set_model(lang_model)
        cur_lang = i18n.get_language()
        row_lang.set_selected(0 if cur_lang == "id" else 1)
        row_lang.connect("notify::selected", self._on_language_changed)
        group_general.add(row_lang)

        page_general.add(group_general)

        # ------------------------------------------
        # Grup 2: Pilihan Modul Tampilan (Modules)
        # ------------------------------------------
        group_modules = Adw.PreferencesGroup()
        group_modules.set_title(_("Display Modules"))
        group_modules.set_description(_("Choose features to show on Dynamic Island."))

        # Media Player Module
        row_media = Adw.ActionRow()
        row_media.set_title(_("🎵 Media Player Controls (YouTube / Spotify)"))
        row_media.set_subtitle(_("Track detection, play/pause buttons, and seekbar"))
        self.sw_media = Gtk.Switch()
        self.sw_media.set_valign(Gtk.Align.CENTER)
        self.sw_media.set_active(config_manager.get("modules", "media_player", True))
        self.sw_media.connect("state-set", lambda sw, s: self._save_module("media_player", s))
        row_media.add_suffix(self.sw_media)
        group_modules.add(row_media)

        # Synced Karaoke Lyrics Module
        row_lyrics = Adw.ActionRow()
        row_lyrics.set_title(_("🎤 Synced Karaoke Lyrics"))
        row_lyrics.set_subtitle(_("Fetch real-time lyrics synchronized per second"))
        self.sw_lyrics = Gtk.Switch()
        self.sw_lyrics.set_valign(Gtk.Align.CENTER)
        self.sw_lyrics.set_active(config_manager.get("modules", "show_synced_lyrics", True))
        self.sw_lyrics.connect("state-set", lambda sw, s: self._save_module("show_synced_lyrics", s))
        row_lyrics.add_suffix(self.sw_lyrics)
        group_modules.add(row_lyrics)

        # Battery / Charger Module
        row_battery = Adw.ActionRow()
        row_battery.set_title(_("⚡ Battery &amp; Charging HUD (UPower)"))
        row_battery.set_subtitle(_("Popup on charger connect/disconnect and low battery"))
        self.sw_battery = Gtk.Switch()
        self.sw_battery.set_valign(Gtk.Align.CENTER)
        self.sw_battery.set_active(config_manager.get("modules", "battery_charging", True))
        self.sw_battery.connect("state-set", lambda sw, s: self._save_module("battery_charging", s))
        row_battery.add_suffix(self.sw_battery)
        group_modules.add(row_battery)

        # Power Profile Module
        row_power = Adw.ActionRow()
        row_power.set_title(_("🍃 Power Profile Switcher (Daemon)"))
        row_power.set_subtitle(_("Quick toggle for Power Saver, Balanced, and Performance modes"))
        self.sw_power = Gtk.Switch()
        self.sw_power.set_valign(Gtk.Align.CENTER)
        self.sw_power.set_active(config_manager.get("modules", "power_profile_switcher", True))
        self.sw_power.connect("state-set", lambda sw, s: self._save_module("power_profile_switcher", s))
        row_power.add_suffix(self.sw_power)
        group_modules.add(row_power)

        # Volume HUD Module
        row_volume = Adw.ActionRow()
        row_volume.set_title(_("🔊 Volume &amp; Mute HUD Indicator"))
        row_volume.set_subtitle(_("HUD popup slider when volume keys are pressed"))
        self.sw_volume = Gtk.Switch()
        self.sw_volume.set_valign(Gtk.Align.CENTER)
        self.sw_volume.set_active(config_manager.get("modules", "volume_hud", True))
        self.sw_volume.connect("state-set", lambda sw, s: self._save_module("volume_hud", s))
        row_volume.add_suffix(self.sw_volume)
        group_modules.add(row_volume)

        # Brightness HUD Module
        row_brightness = Adw.ActionRow()
        row_brightness.set_title(_("☀️ Screen Brightness HUD"))
        row_brightness.set_subtitle(_("HUD popup slider when brightness keys are pressed"))
        self.sw_brightness = Gtk.Switch()
        self.sw_brightness.set_valign(Gtk.Align.CENTER)
        self.sw_brightness.set_active(config_manager.get("modules", "brightness_hud", True))
        self.sw_brightness.connect("state-set", lambda sw, s: self._save_module("brightness_hud", s))
        row_brightness.add_suffix(self.sw_brightness)
        group_modules.add(row_brightness)

        # System Notifications HUD Module
        row_notif = Adw.ActionRow()
        row_notif.set_title(_("🔔 System Notifications HUD"))
        row_notif.set_subtitle(_("Display incoming desktop notifications on the island"))
        self.sw_notif = Gtk.Switch()
        self.sw_notif.set_valign(Gtk.Align.CENTER)
        self.sw_notif.set_active(config_manager.get("modules", "system_notifications", True))
        self.sw_notif.connect("state-set", lambda sw, s: self._save_module("system_notifications", s))
        row_notif.add_suffix(self.sw_notif)
        group_modules.add(row_notif)

        # Bluetooth & TWS Headphone HUD Module
        row_bluetooth = Adw.ActionRow()
        row_bluetooth.set_title(_("🎧 Bluetooth &amp; TWS Headphone HUD"))
        row_bluetooth.set_subtitle(_("Display connection status and battery percentage when Bluetooth devices connect"))
        self.sw_bluetooth = Gtk.Switch()
        self.sw_bluetooth.set_valign(Gtk.Align.CENTER)
        self.sw_bluetooth.set_active(config_manager.get("modules", "bluetooth_hud", True))
        self.sw_bluetooth.connect("state-set", lambda sw, s: self._save_module("bluetooth_hud", s))
        row_bluetooth.add_suffix(self.sw_bluetooth)
        group_modules.add(row_bluetooth)

        page_general.add(group_modules)

        # ------------------------------------------
        # Grup 3: Posisi dan Animasi (Appearance)
        # ------------------------------------------
        group_appearance = Adw.PreferencesGroup()
        group_appearance.set_title(_("Position &amp; Animation"))
        group_appearance.set_description(_("Configure vertical offset, screen selection, and HUD timeout."))

        # Monitor / Display Selector
        row_monitor = Adw.ComboRow()
        row_monitor.set_title(_("Select Display / Monitor"))
        row_monitor.set_subtitle(_("Choose monitor where Dynamic Island will appear"))

        display = Gdk.Display.get_default()
        monitor_names = []
        if display:
            monitors = display.get_monitors()
            for i in range(monitors.get_n_items()):
                m = monitors.get_item(i)
                geom = m.get_geometry()
                connector = m.get_connector() if hasattr(m, 'get_connector') else ""
                label = f"Layar {i + 1}" if cur_lang == "id" else f"Display {i + 1}"
                if connector:
                    label += f" ({connector} - {geom.width}x{geom.height})"
                else:
                    label += f" ({geom.width}x{geom.height})"
                monitor_names.append(label)

        if not monitor_names:
            monitor_names = ["Layar 1 (Utama)" if cur_lang == "id" else "Display 1 (Primary)"]

        str_list = Gtk.StringList.new(monitor_names)
        row_monitor.set_model(str_list)

        curr_mon = config_manager.get("appearance", "monitor_index", 0)
        if 0 <= curr_mon < len(monitor_names):
            row_monitor.set_selected(curr_mon)
        else:
            row_monitor.set_selected(0)

        row_monitor.connect("notify::selected", self._on_monitor_changed)
        group_appearance.add(row_monitor)

        # Margin Y Offset Slider
        row_y = Adw.ActionRow()
        row_y.set_title(_("Top Screen Margin (Y Offset)"))
        row_y.set_subtitle(_("Adjust vertical gap from top edge of monitor"))
        curr_y = config_manager.get("appearance", "y_offset", 8)
        scale_y = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 40, 1)
        scale_y.set_value(curr_y)
        scale_y.set_size_request(160, -1)
        scale_y.set_valign(Gtk.Align.CENTER)
        scale_y.connect("value-changed", self._on_y_offset_changed)
        row_y.add_suffix(scale_y)
        group_appearance.add(row_y)

        # Compact Micro-Pill Switch
        row_micro = Adw.ActionRow()
        row_micro.set_title(_("Compact Micro-Pill Mode (115px)"))
        row_micro.set_subtitle(_("Slim during idle, expands only on mouse hover or track change"))
        self.sw_micro = Gtk.Switch()
        self.sw_micro.set_valign(Gtk.Align.CENTER)
        self.sw_micro.set_active(config_manager.get("appearance", "compact_micro_pill", True))
        self.sw_micro.connect("state-set", self._on_micro_pill_toggled)
        row_micro.add_suffix(self.sw_micro)
        group_appearance.add(row_micro)

        # HUD Timeout Slider
        row_timeout = Adw.ActionRow()
        row_timeout.set_title(_("HUD Popup Duration (Seconds)"))
        row_timeout.set_subtitle(_("How long volume and battery popups remain visible"))
        curr_timeout = config_manager.get("appearance", "hud_timeout_seconds", 3.0)
        scale_timeout = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1.5, 6.0, 0.5)
        scale_timeout.set_value(curr_timeout)
        scale_timeout.set_size_request(160, -1)
        scale_timeout.set_valign(Gtk.Align.CENTER)
        scale_timeout.connect("value-changed", self._on_timeout_changed)
        row_timeout.add_suffix(scale_timeout)
        group_appearance.add(row_timeout)

        page_general.add(group_appearance)
        self.add(page_general)

        # ==========================================
        # PAGE 2: About & Community (Open Source Info)
        # ==========================================
        page_about = Adw.PreferencesPage()
        page_about.set_title(_("About &amp; Community"))
        page_about.set_icon_name("help-about-symbolic")

        # Grup 1: Informasi Aplikasi & Lisensi
        group_app_info = Adw.PreferencesGroup()
        group_app_info.set_title(_("Mint-Island Desktop"))
        group_app_info.set_description(_("Native Dynamic Island for Linux Mint (Cinnamon DE)"))

        row_version = Adw.ActionRow()
        row_version.set_title(_("Version"))
        row_version.set_subtitle("v1.0.0 (Community Edition - 100% Free & Open Source)")
        group_app_info.add(row_version)

        row_license = Adw.ActionRow()
        row_license.set_title(_("License"))
        row_license.set_subtitle("GNU General Public License v3.0 (GPLv3)")
        group_app_info.add(row_license)

        row_author = Adw.ActionRow()
        row_author.set_title(_("Developer &amp; Maintainer"))
        row_author.set_subtitle("Muhammad Yusuf")
        group_app_info.add(row_author)

        page_about.add(group_app_info)

        # Grup 2: Komunitas & Kode Sumber (GitHub)
        group_community = Adw.PreferencesGroup()
        group_community.set_title(_("Source Code &amp; Community"))
        group_community.set_description(_("Contribute, report bugs, or star the project on GitHub"))

        row_github = Adw.ActionRow()
        row_github.set_title("GitHub Repository")
        row_github.set_subtitle("muhammadyusuftechid-star/mint-island")
        btn_github = Gtk.Button(label=_("Visit GitHub"))
        btn_github.set_valign(Gtk.Align.CENTER)
        btn_github.connect("clicked", lambda b: Gio.AppInfo.launch_default_for_uri("https://github.com/muhammadyusuftechid-star/mint-island", None))
        row_github.add_suffix(btn_github)
        group_community.add(row_github)

        row_issues = Adw.ActionRow()
        row_issues.set_title(_("Report an Issue"))
        row_issues.set_subtitle(_("Submit bug reports or suggest new features"))
        btn_issues = Gtk.Button(label=_("Open Issues"))
        btn_issues.set_valign(Gtk.Align.CENTER)
        btn_issues.connect("clicked", lambda b: Gio.AppInfo.launch_default_for_uri("https://github.com/muhammadyusuftechid-star/mint-island/issues", None))
        row_issues.add_suffix(btn_issues)
        group_community.add(row_issues)

        page_about.add(group_community)

        # Grup 3: Developer & Supporter Token (Opsional)
        group_activate = Adw.PreferencesGroup()
        group_activate.set_title(_("Developer &amp; Supporter Token"))
        group_activate.set_description(_("Optional activation token for developers or project sponsors"))

        self.row_edition = Adw.ActionRow()
        self.row_edition.set_title(_("Status"))
        group_activate.add(self.row_edition)

        self.entry_key = Adw.EntryRow()
        self.entry_key.set_title(_("Token / Key"))
        self.entry_key.set_show_apply_button(True)
        self.entry_key.connect("apply", lambda e: self._on_activate_clicked(None))
        group_activate.add(self.entry_key)

        box_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_actions.set_margin_top(8)
        box_actions.set_margin_bottom(8)

        self.btn_activate = Gtk.Button(label=_("Activate Token"))
        self.btn_activate.add_css_class("suggested-action")
        self.btn_activate.connect("clicked", self._on_activate_clicked)
        box_actions.append(self.btn_activate)

        self.btn_deactivate = Gtk.Button(label=_("Reset"))
        self.btn_deactivate.add_css_class("destructive-action")
        self.btn_deactivate.connect("clicked", self._on_deactivate_clicked)
        box_actions.append(self.btn_deactivate)

        self.lbl_license_msg = Gtk.Label(label="")
        self.lbl_license_msg.set_halign(Gtk.Align.START)
        self.lbl_license_msg.set_valign(Gtk.Align.CENTER)
        self.lbl_license_msg.set_hexpand(True)
        box_actions.append(self.lbl_license_msg)

        group_activate.add(box_actions)
        page_about.add(group_activate)

        self.add(page_about)

        # Update initial license view
        self._update_license_display()

    def _update_license_display(self):
        """Refreshes the license status UI based on license_manager."""
        info = license_manager.get_info()
        is_pro = info.get("is_pro", False)
        if is_pro:
            tier_name = info.get("tier", "Community Edition")
            self.row_edition.set_subtitle(f"{_('Community Edition (Full Features Unlocked)')} ({tier_name})")
            self.btn_deactivate.set_sensitive(True)
            self.btn_activate.set_sensitive(False)
            self.entry_key.set_text(info.get('masked_key', 'FREE-FOSS-UNLOCKED'))
            self.entry_key.set_sensitive(False)
        else:
            self.row_edition.set_subtitle(_("Free Trial / Community Edition"))
            self.btn_deactivate.set_sensitive(False)
            self.btn_activate.set_sensitive(True)
            self.entry_key.set_sensitive(True)

    def _on_activate_clicked(self, widget):
        key = self.entry_key.get_text().strip()
        if not key:
            self.lbl_license_msg.set_label("⚠️ Kunci lisensi tidak boleh kosong.")
            return

        self.btn_activate.set_sensitive(False)
        self.lbl_license_msg.set_label("⏳ Sedang memverifikasi lisensi...")

        def _on_result(success: bool, msg: str):
            def _ui_update():
                self.lbl_license_msg.set_label(f"{'✅' if success else '❌'} {msg}")
                self._update_license_display()
                if self.on_config_changed_cb:
                    self.on_config_changed_cb("license_status", success)
                return False
            GLib.idle_add(_ui_update)

        license_manager.activate_async(key, _on_result)

    def _on_deactivate_clicked(self, widget):
        license_manager.deactivate()
        self.lbl_license_msg.set_label("ℹ️ Lisensi telah dinonaktifkan.")
        self.entry_key.set_text("")
        self._update_license_display()
        if self.on_config_changed_cb:
            self.on_config_changed_cb("license_status", False)

    def _on_language_changed(self, combo_row, param):
        idx = combo_row.get_selected()
        new_lang = "id" if idx == 0 else "en"
        i18n.set_language(new_lang)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("language", new_lang)

    def _on_enabled_toggled(self, switch, state):
        config_manager.set("general", "enabled", state)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("enabled", state)
        return False

    def _on_autostart_toggled(self, switch, state):
        if state:
            AutostartManager.enable()
        else:
            AutostartManager.disable()
        config_manager.set("general", "autostart_on_boot", state)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("autostart", state)
        return False

    def _save_module(self, module_name: str, state: bool):
        config_manager.set("modules", module_name, state)
        if self.on_config_changed_cb:
            self.on_config_changed_cb(f"module_{module_name}", state)
        return False

    def _on_y_offset_changed(self, scale):
        val = int(scale.get_value())
        config_manager.set("appearance", "y_offset", val)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("y_offset", val)

    def _on_timeout_changed(self, scale):
        val = round(scale.get_value(), 1)
        config_manager.set("appearance", "hud_timeout_seconds", val)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("hud_timeout", val)

    def _on_monitor_changed(self, combo_row, param):
        idx = combo_row.get_selected()
        config_manager.set("appearance", "monitor_index", idx)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("monitor_index", idx)

    def _on_micro_pill_toggled(self, sw, state):
        config_manager.set("appearance", "compact_micro_pill", state)
        if self.on_config_changed_cb:
            self.on_config_changed_cb("compact_micro_pill", state)
        return False
