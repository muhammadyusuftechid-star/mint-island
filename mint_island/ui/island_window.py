"""
Main Dynamic Island Window for Linux Mint Cinnamon (GTK4 + X11)
Includes Persistent Hardware Indicators, Control Center Dashboard,
Hardware HUD Listeners, YouTube/MPRIS Media Player, and Real-Time Synced Lyrics.
"""
import time
import subprocess
import logging
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GdkX11', '4.0')
from gi.repository import Gtk, Gdk, GdkX11, GLib, Pango

from typing import Final, Optional, Tuple, Literal

from mint_island.config import config_manager
from mint_island.autostart import AutostartManager
from mint_island.modules.battery_module import BatteryMonitor
from mint_island.modules.volume_module import VolumeMonitor
from mint_island.modules.brightness_module import BrightnessMonitor
from mint_island.modules.mpris_module import MPRISMonitor
from mint_island.modules.lyrics_module import LyricsEngine
from mint_island.modules.power_module import PowerProfileMonitor
from mint_island.modules.notification_module import NotificationMonitor
from mint_island.modules.bluetooth_module import BluetoothMonitor
from mint_island.license import license_manager
from mint_island.i18n import _

class IslandDimensions:
    """Fixed UI geometry constants (avoids scattered magic numbers)."""
    PILL_MICRO_WIDTH: Final[int] = 120      # Ultra-compact micro-notch for idle (unobtrusive)
    PILL_PEEK_WIDTH: Final[int] = 360       # Peek width on hover or song change
    PILL_IDLE_WIDTH: Final[int] = 300       # Legacy wide idle width (if micro mode disabled)
    PILL_MEDIA_WIDTH: Final[int] = 380      # Legacy wide media width
    HUD_WIDTH: Final[int] = 280
    NOTIFICATION_WIDTH: Final[int] = 360    # Desktop notification pill banner
    CARD_WIDTH: Final[int] = 400
    CARD_HEIGHT_FULL: Final[int] = 430      # Media + lyrics + hardware + power profile
    CARD_HEIGHT_MEDIA: Final[int] = 355     # Media + hardware + power profile (no lyrics)
    CARD_HEIGHT_DASHBOARD: Final[int] = 295 # Pure hardware + power profile control center
    BAR_HEIGHT: Final[int] = 34             # Sleek 34px bar height
    BT_ROW_HEIGHT: Final[int] = 34          # Height of Bluetooth device row in Control Center

def format_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"

class IslandWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Mint Island Overlay")
        self.app = app

        self.set_decorated(False)
        self.set_resizable(True)
        self.set_focusable(False)
        self.add_css_class("island-window")

        # Window state and cached geometry for minimal X11 calls
        self.state: Literal["idle", "hud", "expanded", "notification"] = "idle"
        self._last_geometry: Optional[Tuple[int, int, int, int]] = None
        self.xid: Optional[int] = None
        self.hud_timer_id: Optional[int] = None
        self.notif_timer_id: Optional[int] = None

        # Hover & Auto-Peek state for Micro-Pill mode
        self.is_hovered = False
        self.is_peeked = False
        self._leave_timer_id: Optional[int] = None
        self._initial_mpris_settled = False
        self.song_peek_timer_id: Optional[int] = None
        self._last_peek_title = ""

        # Internal slider sync flags (prevent feedback loops)
        self._syncing_vol_slider = False
        self._syncing_bright_slider = False

        # Media & Lyrics State
        self.lyrics_engine = LyricsEngine()
        self.media_playing = False
        self.media_duration = 0.0
        self._is_seeking = False

        # Load Stylesheet
        self._load_styles()

        # Build UI Elements
        self._build_ui()

        # Click gesture scoped strictly to capsule to expand into Control Center
        capsule_gesture = Gtk.GestureClick()
        capsule_gesture.connect("released", self._on_capsule_clicked)
        self.capsule.add_controller(capsule_gesture)

        # Hover motion controller attached to top-level window for whole-surface detection
        window_motion = Gtk.EventControllerMotion()
        window_motion.connect("enter", self._on_capsule_enter)
        window_motion.connect("motion", self._on_capsule_enter)
        window_motion.connect("leave", self._on_capsule_leave)
        self.add_controller(window_motion)

        # Key controller for Escape key to collapse expanded card
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)

        # Connect map event to configure X11 window hints
        self.connect("realize", self._on_realize)

        # Clock timer (updates every 1000ms)
        GLib.timeout_add(1000, self._update_clock)

        # Monitor change listener (for dynamic plugging/unplugging)
        display = Gdk.Display.get_default()
        if display:
            monitors = display.get_monitors()
            if hasattr(monitors, "connect"):
                monitors.connect("items-changed", lambda *_: GLib.idle_add(self.reposition))

        # Initialize Hardware & Media Monitors
        self._init_monitors()

    def _load_styles(self):
        """Loads styles.css into Gdk Display."""
        css_file = Path(__file__).parent / "styles.css"
        if not css_file.exists():
            css_file = Path("/usr/share/mint-island/mint_island/ui/styles.css")
        if css_file.exists():
            provider = Gtk.CssProvider()
            provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _build_ui(self):
        """Builds the persistent capsule, HUD container, and expanded Control Center card."""
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.root_box)

        # ==========================================
        # 1. Compact Capsule (Always Visible Top Pill)
        # ==========================================
        self.capsule = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.capsule.add_css_class("island-capsule")
        initial_w = IslandDimensions.PILL_MICRO_WIDTH if config_manager.get("appearance", "compact_micro_pill", True) else IslandDimensions.PILL_IDLE_WIDTH
        self.capsule.set_size_request(initial_w, IslandDimensions.BAR_HEIGHT)

        self.badge = Gtk.Label(label="●")
        self.badge.add_css_class("island-badge")

        self.clock_label = Gtk.Label(label=time.strftime("%H:%M"))
        self.clock_label.add_css_class("island-clock")

        # Mini music/status icon in micro-pill mode
        self.pill_micro_icon = Gtk.Label(label="🎵")
        self.pill_micro_icon.add_css_class("pill-micro-icon")
        self.pill_micro_icon.set_visible(False)

        self.title_label = Gtk.Label(label="Mint Island")
        self.title_label.add_css_class("island-title")

        # Mini music/lyric subtitle in capsule (appears when media plays)
        self.pill_lyric_label = Gtk.Label(label="")
        self.pill_lyric_label.add_css_class("pill-lyric")
        self.pill_lyric_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.pill_lyric_label.set_max_width_chars(20)
        self.pill_lyric_label.set_visible(False)

        # Persistent Hardware Indicators in Capsule (Battery, Power Saver & Volume directly visible!)
        self.pill_hw_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.pill_hw_box.add_css_class("pill-hw-box")

        self.pill_power_lbl = Gtk.Label(label="🍃")
        self.pill_power_lbl.add_css_class("pill-power-saver-badge")
        self.pill_power_lbl.set_visible(False)

        self.pill_battery_lbl = Gtk.Label(label="⚡ --%")
        self.pill_battery_lbl.add_css_class("pill-hw-label")

        self.pill_vol_lbl = Gtk.Label(label="🔊 --%")
        self.pill_vol_lbl.add_css_class("pill-hw-label")

        self.pill_hw_box.append(self.pill_power_lbl)
        self.pill_hw_box.append(self.pill_battery_lbl)
        self.pill_hw_box.append(self.pill_vol_lbl)

        self.capsule.append(self.badge)
        self.capsule.append(self.clock_label)
        self.capsule.append(self.pill_micro_icon)
        self.capsule.append(self.title_label)
        self.capsule.append(self.pill_lyric_label)
        self.capsule.append(self.pill_hw_box)

        # ==========================================
        # 2. Hardware HUD Container (Auto-Popup 3s)
        # ==========================================
        self.hud_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.hud_box.add_css_class("island-hud")
        self.hud_box.set_size_request(IslandDimensions.HUD_WIDTH, IslandDimensions.BAR_HEIGHT)
        self.hud_box.set_visible(False)

        self.hud_icon = Gtk.Label(label="🔊")
        self.hud_icon.add_css_class("hud-icon")

        self.hud_label = Gtk.Label(label="Volume")
        self.hud_label.add_css_class("hud-label")
        self.hud_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.hud_label.set_max_width_chars(16)

        self.hud_progress = Gtk.ProgressBar()
        self.hud_progress.add_css_class("hud-progress")
        self.hud_progress.set_hexpand(True)
        self.hud_progress.set_valign(Gtk.Align.CENTER)

        self.hud_percent = Gtk.Label(label="50%")
        self.hud_percent.add_css_class("hud-percent")

        self.hud_box.append(self.hud_icon)
        self.hud_box.append(self.hud_label)
        self.hud_box.append(self.hud_progress)
        self.hud_box.append(self.hud_percent)

        # ==========================================
        # 2B. Desktop Notification Pill Container
        # ==========================================
        self.notification_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.notification_box.add_css_class("island-notification")
        self.notification_box.set_size_request(IslandDimensions.NOTIFICATION_WIDTH, IslandDimensions.BAR_HEIGHT)
        self.notification_box.set_visible(False)

        self.notif_icon = Gtk.Label(label="🔔")
        self.notif_icon.add_css_class("notif-icon")
        self.notif_icon.set_valign(Gtk.Align.CENTER)

        notif_text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        notif_text_box.set_hexpand(True)
        notif_text_box.set_valign(Gtk.Align.CENTER)

        self.notif_title = Gtk.Label(label="")
        self.notif_title.add_css_class("notif-title")
        self.notif_title.set_halign(Gtk.Align.START)
        self.notif_title.set_ellipsize(3)
        self.notif_title.set_max_width_chars(24)

        self.notif_body = Gtk.Label(label="")
        self.notif_body.add_css_class("notif-body")
        self.notif_body.set_halign(Gtk.Align.START)
        self.notif_body.set_ellipsize(3)
        self.notif_body.set_max_width_chars(28)

        notif_text_box.append(self.notif_title)
        notif_text_box.append(self.notif_body)

        self.notif_close_btn = Gtk.Button(label="✕")
        self.notif_close_btn.add_css_class("notif-close-btn")
        self.notif_close_btn.set_valign(Gtk.Align.CENTER)
        self.notif_close_btn.connect("clicked", lambda b: self._on_notification_timeout())

        self.notification_box.append(self.notif_icon)
        self.notification_box.append(notif_text_box)
        self.notification_box.append(self.notif_close_btn)

        notif_gesture = Gtk.GestureClick()
        notif_gesture.connect("released", lambda *_: self._on_notification_timeout())
        self.notification_box.add_controller(notif_gesture)

        # ==========================================
        # 3. Expanded Card (Full Control Center Dashboard)
        # ==========================================
        self.expanded_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.expanded_card.add_css_class("island-card-expanded")
        self.expanded_card.set_visible(False)
        self.expanded_card.set_size_request(IslandDimensions.CARD_WIDTH, IslandDimensions.CARD_HEIGHT_FULL)

        # --- A. Card Header Row ---
        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_icon = Gtk.Label(label="🏝️")
        header_icon.set_valign(Gtk.Align.CENTER)

        header_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        header_info.set_hexpand(True)
        self.card_heading_lbl = Gtk.Label(label="Mint Island Control")
        self.card_heading_lbl.add_css_class("card-heading")
        self.card_heading_lbl.set_halign(Gtk.Align.START)

        self.card_date_lbl = Gtk.Label(label=time.strftime("%A, %d %b • %H:%M"))
        self.card_date_lbl.add_css_class("card-subtext")
        self.card_date_lbl.set_halign(Gtk.Align.START)

        header_info.append(self.card_heading_lbl)
        header_info.append(self.card_date_lbl)

        chip_label = "PRO 🌟" if license_manager.is_pro() else "ACTIVE"
        self.chip = Gtk.Label(label=chip_label)
        self.chip.add_css_class("status-chip")
        self.chip.set_valign(Gtk.Align.CENTER)

        self.btn_collapse = Gtk.Button(label="✕")
        self.btn_collapse.add_css_class("card-close-btn")
        self.btn_collapse.set_valign(Gtk.Align.CENTER)
        self.btn_collapse.connect("clicked", lambda _: self.collapse_to_idle())

        header_row.append(header_icon)
        header_row.append(header_info)
        header_row.append(self.chip)
        header_row.append(self.btn_collapse)

        # --- B. Media Player Section (YouTube / Spotify) ---
        self.media_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        track_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.media_icon = Gtk.Label(label="🎵")
        self.media_icon.set_valign(Gtk.Align.START)

        track_meta = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        track_meta.set_hexpand(True)
        self.media_title_lbl = Gtk.Label(label="Tidak ada media diputar")
        self.media_title_lbl.add_css_class("media-title")
        self.media_title_lbl.set_halign(Gtk.Align.START)
        self.media_title_lbl.set_ellipsize(3)
        self.media_title_lbl.set_max_width_chars(28)

        self.media_artist_lbl = Gtk.Label(label="YouTube / Spotify / VLC")
        self.media_artist_lbl.add_css_class("media-artist")
        self.media_artist_lbl.set_halign(Gtk.Align.START)

        track_meta.append(self.media_title_lbl)
        track_meta.append(self.media_artist_lbl)
        track_row.append(self.media_icon)
        track_row.append(track_meta)

        # Seekbar Row
        seek_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.media_seekbar = Gtk.ProgressBar()
        self.media_seekbar.add_css_class("media-seekbar")
        self.media_seekbar.set_fraction(0.0)

        seek_click = Gtk.GestureClick()
        seek_click.connect("pressed", self._on_seekbar_seek)
        self.media_seekbar.add_controller(seek_click)

        seek_drag = Gtk.GestureDrag()
        seek_drag.connect("drag-update", self._on_seekbar_drag)
        seek_drag.connect("drag-end", self._on_seekbar_drag_end)
        self.media_seekbar.add_controller(seek_drag)

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.media_time_lbl = Gtk.Label(label="00:00 / 00:00")
        self.media_time_lbl.add_css_class("media-time")
        self.media_time_lbl.set_hexpand(True)
        self.media_time_lbl.set_halign(Gtk.Align.END)
        time_box.append(self.media_time_lbl)

        seek_box.append(self.media_seekbar)
        seek_box.append(time_box)

        # Controls Row (Previous, Play/Pause, Next)
        controls_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        controls_row.set_halign(Gtk.Align.CENTER)

        self.btn_prev = Gtk.Button(label="⏮")
        self.btn_prev.add_css_class("media-btn")
        self.btn_prev.connect("clicked", lambda b: self.mpris_monitor.previous())

        self.btn_play_pause = Gtk.Button(label="▶")
        self.btn_play_pause.add_css_class("media-btn")
        self.btn_play_pause.add_css_class("media-btn-primary")
        self.btn_play_pause.connect("clicked", lambda b: self.mpris_monitor.play_pause())

        self.btn_next = Gtk.Button(label="⏭")
        self.btn_next.add_css_class("media-btn")
        self.btn_next.connect("clicked", lambda b: self.mpris_monitor.next())

        controls_row.append(self.btn_prev)
        controls_row.append(self.btn_play_pause)
        controls_row.append(self.btn_next)

        # Karaoke Lyrics Box
        self.karaoke_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.karaoke_box.add_css_class("karaoke-container")
        self.karaoke_box.set_visible(config_manager.get("modules", "show_synced_lyrics", True))

        self.lyric_line_prev = Gtk.Label(label="")
        self.lyric_line_prev.add_css_class("lyric-line-inactive")
        self.lyric_line_prev.set_ellipsize(3)

        self.lyric_line_active = Gtk.Label(label="🎵 Putar lagu di YouTube atau Spotify untuk lirik")
        self.lyric_line_active.add_css_class("lyric-line-active")
        self.lyric_line_active.set_ellipsize(3)

        self.lyric_line_next = Gtk.Label(label="")
        self.lyric_line_next.add_css_class("lyric-line-inactive")
        self.lyric_line_next.set_ellipsize(3)

        self.karaoke_box.append(self.lyric_line_prev)
        self.karaoke_box.append(self.lyric_line_active)
        self.karaoke_box.append(self.lyric_line_next)

        self.media_section.append(track_row)
        self.media_section.append(seek_box)
        self.media_section.append(controls_row)
        self.media_section.append(self.karaoke_box)

        # --- C. Quick Hardware Control Panel (Always Visible in Expanded Card!) ---
        self.hw_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.hw_panel.add_css_class("hw-control-panel")

        # 1. Battery Status Row
        bat_header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.card_bat_lbl = Gtk.Label(label="🔋 Baterai: --%")
        self.card_bat_lbl.add_css_class("hw-label-text")
        self.card_bat_lbl.set_halign(Gtk.Align.START)
        self.card_bat_lbl.set_hexpand(True)

        self.card_bat_sub = Gtk.Label(label="Daya Baterai")
        self.card_bat_sub.add_css_class("card-subtext")
        self.card_bat_sub.set_halign(Gtk.Align.END)

        bat_header_row.append(self.card_bat_lbl)
        bat_header_row.append(self.card_bat_sub)

        self.card_bat_bar = Gtk.ProgressBar()
        self.card_bat_bar.add_css_class("hw-battery-bar")
        self.card_bat_bar.set_fraction(0.5)

        self.card_bat_est_lbl = Gtk.Label(label="")
        self.card_bat_est_lbl.add_css_class("card-bat-est-lbl")
        self.card_bat_est_lbl.set_halign(Gtk.Align.START)

        # Power Profile Mode Buttons Row
        self.power_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.power_row.add_css_class("power-profile-row")

        self.power_lbl = Gtk.Label(label=_("Power Mode"))
        self.power_lbl.add_css_class("hw-label-text")
        self.power_lbl.set_halign(Gtk.Align.START)
        self.power_row.append(self.power_lbl)

        self.btn_power_saver = Gtk.Button(label="🍃 " + _("Power Saver"))
        self.btn_power_saver.add_css_class("power-profile-btn")
        self.btn_power_saver.connect("clicked", lambda b: self._set_power_profile("power-saver"))

        self.btn_power_balanced = Gtk.Button(label="⚖️ " + _("Balanced"))
        self.btn_power_balanced.add_css_class("power-profile-btn")
        self.btn_power_balanced.connect("clicked", lambda b: self._set_power_profile("balanced"))

        self.btn_power_perf = Gtk.Button(label="🚀 " + _("Performance"))
        self.btn_power_perf.add_css_class("power-profile-btn")
        self.btn_power_perf.connect("clicked", lambda b: self._set_power_profile("performance"))

        self.power_row.append(self.btn_power_saver)
        self.power_row.append(self.btn_power_balanced)
        self.power_row.append(self.btn_power_perf)
        self.power_row.set_visible(config_manager.get("modules", "power_profile_switcher", True))

        # 2. Interactive Volume Slider Row
        vol_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vol_row.add_css_class("hw-row")

        self.vol_mute_btn = Gtk.Button(label="🔊")
        self.vol_mute_btn.add_css_class("hw-icon-btn")
        self.vol_mute_btn.connect("clicked", self._on_mute_clicked)

        vol_lbl = Gtk.Label(label=_("Volume"))
        vol_lbl.add_css_class("hw-label-text")
        vol_lbl.set_halign(Gtk.Align.START)

        self.vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.vol_scale.set_draw_value(False)
        self.vol_scale.set_hexpand(True)
        self.vol_scale.add_css_class("hw-slider")
        self.vol_scale.add_css_class("hw-slider-volume")
        self.vol_scale.connect("value-changed", self._on_vol_scale_changed)

        self.vol_value_lbl = Gtk.Label(label="50%")
        self.vol_value_lbl.add_css_class("hw-val-text")

        vol_row.append(self.vol_mute_btn)
        vol_row.append(vol_lbl)
        vol_row.append(self.vol_scale)
        vol_row.append(self.vol_value_lbl)

        # 3. Interactive Brightness Slider Row
        bright_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bright_row.add_css_class("hw-row")

        bright_icon = Gtk.Label(label="☀️")
        bright_icon.add_css_class("hw-icon-btn")

        bright_lbl = Gtk.Label(label=_("Brightness"))
        bright_lbl.add_css_class("hw-label-text")
        bright_lbl.set_halign(Gtk.Align.START)

        self.bright_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 1)
        self.bright_scale.set_draw_value(False)
        self.bright_scale.set_hexpand(True)
        self.bright_scale.add_css_class("hw-slider")
        self.bright_scale.add_css_class("hw-slider-brightness")
        self.bright_scale.connect("value-changed", self._on_bright_scale_changed)

        self.bright_value_lbl = Gtk.Label(label="60%")
        self.bright_value_lbl.add_css_class("hw-val-text")

        bright_row.append(bright_icon)
        bright_row.append(bright_lbl)
        bright_row.append(self.bright_scale)
        bright_row.append(self.bright_value_lbl)

        # 4. Connected Bluetooth Devices Box
        self.card_bt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.card_bt_box.set_visible(False)

        self.hw_panel.append(bat_header_row)
        self.hw_panel.append(self.card_bat_bar)
        self.hw_panel.append(self.card_bat_est_lbl)
        self.hw_panel.append(self.power_row)
        self.hw_panel.append(vol_row)
        self.hw_panel.append(bright_row)
        self.hw_panel.append(self.card_bt_box)

        # --- D. Card Bottom Footer Row ---
        footer_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer_row.set_halign(Gtk.Align.END)
        self.btn_settings = Gtk.Button(label="⚙️ " + _("Settings"))
        self.btn_settings.add_css_class("btn-open-settings")
        self.btn_settings.connect("clicked", self._on_settings_clicked)
        footer_row.append(self.btn_settings)

        # Assemble into Expanded Card
        self.expanded_card.append(header_row)
        self.expanded_card.append(self.media_section)
        self.expanded_card.append(self.hw_panel)
        self.expanded_card.append(footer_row)

        # Add all major containers to root box
        self.root_box.append(self.capsule)
        self.root_box.append(self.hud_box)
        self.root_box.append(self.notification_box)
        self.root_box.append(self.expanded_card)

    def _init_monitors(self):
        """Initializes all hardware and media listeners and populates initial values."""
        try:
            self.battery_monitor = BatteryMonitor(self._on_battery_event)
            self.volume_monitor = VolumeMonitor(self._on_volume_event)
            self.brightness_monitor = BrightnessMonitor(self._on_brightness_event)
            self.power_monitor = PowerProfileMonitor(self._on_power_profile_changed)
            self.notification_monitor = NotificationMonitor(self._on_notification_event)
            self.bluetooth_monitor = BluetoothMonitor(self._on_bluetooth_event)
            self.mpris_monitor = MPRISMonitor(
                on_track_change_cb=self._on_track_change,
                on_position_tick_cb=self._on_position_tick
            )

            # Paint initial hardware stats immediately to capsule and card
            self._update_bluetooth_status()
            if hasattr(self, 'power_monitor'):
                self._on_power_profile_changed(self.power_monitor.active_profile)
            if hasattr(self, 'battery_monitor'):
                self._on_battery_event(
                    self.battery_monitor.is_charging,
                    self.battery_monitor.percentage,
                    False,
                    False
                )
            if hasattr(self, 'volume_monitor'):
                self._on_volume_event(
                    self.volume_monitor.current_volume,
                    self.volume_monitor.is_muted,
                    trigger_hud=False
                )
            if hasattr(self, 'brightness_monitor'):
                self._on_brightness_event(self.brightness_monitor.current_brightness, trigger_hud=False)

        except Exception as e:
            logging.error(f"Error initializing monitors: {e}")

    # ==========================================
    # MPRIS Media & Karaoke Callbacks
    # ==========================================
    def _on_track_change(self, status, title, artist, art_url, duration_sec, pos_sec):
        """Called when song/media changes in YouTube/Spotify."""
        self.media_playing = (status == "Playing")
        self.media_duration = duration_sec

        self.btn_play_pause.set_label("⏸" if self.media_playing else "▶")

        has_media_player = config_manager.get("modules", "media_player", True)
        has_lyrics = config_manager.get("modules", "show_synced_lyrics", True)

        if title and has_media_player:
            clean_artist, clean_title = self.lyrics_engine.clean_youtube_title(title)
            display_artist = artist if artist else clean_artist
            display_title = clean_title if clean_title else title

            self.media_title_lbl.set_label(display_title)
            self.media_artist_lbl.set_label(display_artist if display_artist else "YouTube Media")

            if has_lyrics:
                self.lyrics_engine.fetch_lyrics_async(
                    artist=display_artist,
                    title=display_title,
                    callback=self._on_lyrics_loaded
                )
            else:
                self.lyric_line_active.set_label(f"🎤 {_('Lyrics disabled in Settings')}")
                self.lyric_line_prev.set_label("")
                self.lyric_line_next.set_label("")
        else:
            self.lyrics_engine.clear()
            self.media_title_lbl.set_label(_("No media playing"))
            self.media_artist_lbl.set_label("YouTube / Spotify / VLC")
            self.lyric_line_active.set_label(f"🎵 {_('Ready to detect media...')}")
            self.lyric_line_prev.set_label("")
            self.lyric_line_next.set_label("")

        # Update Compact Capsule
        is_media_active = (status in ("Playing", "Paused")) and bool(title) and has_media_player
        if is_media_active:
            icon = "🎵" if self.media_playing else "⏸"
            self.pill_lyric_label.set_label(f"{icon} {title[:20]}")
            self.pill_micro_icon.set_label(icon)

            if not self._initial_mpris_settled:
                self._initial_mpris_settled = True
                self._last_peek_title = title
                self._update_capsule_display()
            elif self.media_playing and title != getattr(self, '_last_peek_title', ''):
                self._last_peek_title = title
                self._trigger_song_peek()
            else:
                self._update_capsule_display()
        else:
            self._update_capsule_display()

        if self.state == "expanded":
            self.media_section.set_visible(is_media_active)
            self.karaoke_box.set_visible(is_media_active and has_lyrics)
            self.reposition()

    def _on_lyrics_loaded(self, lyrics_list):
        """Callback when LRCLIB lyrics are loaded."""
        if not lyrics_list:
            GLib.idle_add(self.lyric_line_active.set_label, f"🎤 {_('Lyrics not found in database')}")
        else:
            GLib.idle_add(self.lyric_line_active.set_label, f"🎤 {_('Synchronized lyrics ready')}")

    def _on_position_tick(self, pos_sec):
        """Called every 250ms during active media playback to update seekbar & karaoke."""
        if self.media_duration > 0 and not self._is_seeking:
            fraction = min(1.0, max(0.0, pos_sec / self.media_duration))
            self.media_seekbar.set_fraction(fraction)
            self.media_time_lbl.set_label(f"{format_time(pos_sec)} / {format_time(self.media_duration)}")

        idx, curr_line, next_line = self.lyrics_engine.get_current_lyric(pos_sec)
        if curr_line:
            self.lyric_line_active.set_label(curr_line)
            if idx > 0 and idx - 1 < len(self.lyrics_engine.current_lyrics):
                self.lyric_line_prev.set_label(self.lyrics_engine.current_lyrics[idx - 1][1])
            else:
                self.lyric_line_prev.set_label("")
            self.lyric_line_next.set_label(next_line)

            if self.media_playing and self.state == "idle":
                if config_manager.get("modules", "show_synced_lyrics", True):
                    self.pill_lyric_label.set_label(f"🎵 {curr_line}")
                elif self.mpris_monitor.title:
                    self.pill_lyric_label.set_label(f"🎵 {self.mpris_monitor.title[:20]}")

    # ==========================================
    # Hardware Event Callbacks (Volume, Brightness, Battery)
    # ==========================================
    def _on_volume_event(self, volume, is_muted, trigger_hud=True):
        """Updates persistent capsule, expanded card sliders, and triggers 3s HUD."""
        vol_icon = "🔇" if is_muted else ("🔈" if volume < 30 else ("🔉" if volume < 70 else "🔊"))

        # 1. Update Capsule (Always Visible)
        self.pill_vol_lbl.set_label(vol_icon if is_muted else f"{vol_icon} {volume}%")

        # 2. Update Expanded Card Sliders
        self._syncing_vol_slider = True
        self.vol_scale.set_value(0 if is_muted else volume)
        self.vol_value_lbl.set_label(f"{volume}%" if not is_muted else "Mute")
        self.vol_mute_btn.set_label("🔇" if is_muted else "🔊")
        self._syncing_vol_slider = False

        # 3. Trigger 3-Second Bloom HUD if enabled and not already expanded
        if trigger_hud and config_manager.get("modules", "volume_hud", True) and self.state != "expanded":
            icon = vol_icon
            label = _("Volume") if not is_muted else "Mute"
            percent_str = f"{volume}%" if not is_muted else "0%"
            fraction = 0.0 if is_muted else min(1.0, max(0.0, volume / 100.0))
            color_class = "hud-muted" if is_muted else "hud-volume"
            self.show_hud(icon, label, percent_str, fraction, color_class)

    def _on_brightness_event(self, brightness, trigger_hud=True):
        """Updates expanded card brightness slider and triggers 3s HUD."""
        # 1. Update Expanded Card Sliders
        self._syncing_bright_slider = True
        self.bright_scale.set_value(brightness)
        self.bright_value_lbl.set_label(f"{brightness}%")
        self._syncing_bright_slider = False

        # 2. Trigger 3-Second Bloom HUD if enabled and not already expanded
        if trigger_hud and config_manager.get("modules", "brightness_hud", True) and self.state != "expanded":
            fraction = min(1.0, max(0.0, brightness / 100.0))
            self.show_hud("☀️", _("Brightness"), f"{brightness}%", fraction, "hud-brightness")

    def _on_battery_event(self, is_charging, percentage, is_low, state_changed):
        """Updates persistent capsule battery, expanded card battery, and triggers 3s HUD."""
        bat_icon = "⚡" if is_charging else ("🪫" if is_low else "🔋")

        # 1. Update Capsule Battery Badge & Indicator Dot
        self.badge.set_label("⚡" if is_charging else "●")
        self.pill_battery_lbl.set_label(f"{bat_icon} {percentage}%")
        self.pill_battery_lbl.remove_css_class("pill-bat-charging")
        self.pill_battery_lbl.remove_css_class("pill-bat-low")
        if is_charging:
            self.pill_battery_lbl.add_css_class("pill-bat-charging")
        elif is_low:
            self.pill_battery_lbl.add_css_class("pill-bat-low")

        # 2. Update Expanded Card Battery Status
        bat_status_str = _("Charging (AC)") if is_charging else _("Battery Power")
        self.card_bat_lbl.set_label(f"{bat_icon} {_('Battery')}: {percentage}%")
        self.card_bat_sub.set_label(bat_status_str)
        self.card_bat_bar.set_fraction(min(1.0, max(0.0, percentage / 100.0)))

        for c in ["bat-charging", "bat-normal", "bat-low"]:
            self.card_bat_bar.remove_css_class(c)
        if is_charging:
            self.card_bat_bar.add_css_class("bat-charging")
        elif is_low:
            self.card_bat_bar.add_css_class("bat-low")
        else:
            self.card_bat_bar.add_css_class("bat-normal")

        # Update estimate string under battery bar
        if hasattr(self, 'card_bat_est_lbl') and hasattr(self, 'battery_monitor'):
            self.card_bat_est_lbl.set_label(self.battery_monitor.get_estimate_str())

        # 3. Trigger 3-Second Bloom HUD if enabled and not already expanded
        if config_manager.get("modules", "battery_charging", True) and self.state != "expanded":
            fraction = min(1.0, max(0.0, percentage / 100.0))
            if state_changed:
                if is_charging:
                    self.show_hud("⚡", _("Charging"), f"{percentage}%", fraction, "hud-charging")
                else:
                    self.show_hud("🔋", _("Discharging"), f"{percentage}%", fraction, "hud-volume")
            elif is_low:
                self.show_hud("🪫", _("Battery Low"), f"{percentage}%", fraction, "hud-danger")

    # ==========================================
    # Interactive Slider Controls (User Click & Drag)
    # ==========================================
    def _on_vol_scale_changed(self, scale):
        if self._syncing_vol_slider:
            return
        val = int(scale.get_value())
        self.vol_value_lbl.set_label(f"{val}%")
        self.pill_vol_lbl.set_label(f"🔊 {val}%" if val > 0 else "🔇")
        if hasattr(self, 'volume_monitor'):
            self.volume_monitor.set_volume(val)

    def _on_bright_scale_changed(self, scale):
        if self._syncing_bright_slider:
            return
        val = int(scale.get_value())
        self.bright_value_lbl.set_label(f"{val}%")
        if hasattr(self, 'brightness_monitor'):
            self.brightness_monitor.set_brightness(val)

    def _on_mute_clicked(self, btn):
        if hasattr(self, 'volume_monitor'):
            self.volume_monitor.toggle_mute()
            new_muted = self.volume_monitor.is_muted
            self.vol_mute_btn.set_label("🔇" if new_muted else "🔊")
            self.vol_value_lbl.set_label("Mute" if new_muted else f"{self.volume_monitor.current_volume}%")
            self.pill_vol_lbl.set_label("🔇" if new_muted else f"🔊 {self.volume_monitor.current_volume}%")

    def _on_settings_clicked(self, btn):
        self.collapse_to_idle()
        if hasattr(self, 'app') and hasattr(self.app, 'open_settings'):
            self.app.open_settings()

    # ==========================================
    # Power Profile Control Callbacks
    # ==========================================
    def _on_power_profile_changed(self, profile: str):
        """Updates UI highlight when power profile changes."""
        for b in [self.btn_power_saver, self.btn_power_balanced, self.btn_power_perf]:
            b.remove_css_class("power-btn-active-power-saver")
            b.remove_css_class("power-btn-active-balanced")
            b.remove_css_class("power-btn-active-performance")

        if profile == "power-saver":
            self.btn_power_saver.add_css_class("power-btn-active-power-saver")
            self.pill_power_lbl.set_visible(True)
        elif profile == "performance":
            self.btn_power_perf.add_css_class("power-btn-active-performance")
            self.pill_power_lbl.set_visible(False)
        else:  # balanced
            self.btn_power_balanced.add_css_class("power-btn-active-balanced")
            self.pill_power_lbl.set_visible(False)

    def _set_power_profile(self, profile: str):
        if hasattr(self, 'power_monitor'):
            self.power_monitor.set_profile(profile)

    # ==========================================
    # HUD Display & Auto-Collapse Mechanics
    # ==========================================
    def show_hud(self, icon, label, percent_str, fraction, color_class):
        if self.hud_timer_id is not None:
            GLib.source_remove(self.hud_timer_id)
            self.hud_timer_id = None
        if self.notif_timer_id is not None:
            GLib.source_remove(self.notif_timer_id)
            self.notif_timer_id = None

        self.hud_icon.set_label(icon)
        self.hud_label.set_label(label)
        self.hud_percent.set_label(percent_str)
        self.hud_progress.set_fraction(fraction)

        for c in ["hud-volume", "hud-brightness", "hud-charging", "hud-muted", "hud-danger", "hud-bluetooth"]:
            self.hud_progress.remove_css_class(c)
        self.hud_progress.add_css_class(color_class)

        self.state = "hud"
        self.capsule.set_visible(False)
        self.notification_box.set_visible(False)
        self.expanded_card.set_visible(False)
        self.hud_box.set_visible(True)
        GLib.idle_add(self.reposition)

        timeout_sec = config_manager.get("appearance", "hud_timeout_seconds", 3.0)
        self.hud_timer_id = GLib.timeout_add(int(timeout_sec * 1000), self._on_hud_timeout)

    def _on_hud_timeout(self):
        self.hud_timer_id = None
        self.state = "idle"
        self.hud_box.set_visible(False)
        self.capsule.set_visible(True)
        self._update_capsule_display()
        return False

    # ==========================================
    # Desktop Notification Display & Dismiss
    # ==========================================
    def _on_notification_event(self, app_name, summary, body, app_icon, emoji):
        """Callback when a desktop notification arrives."""
        if not config_manager.get("modules", "system_notifications", True):
            return
        if self.state == "expanded":
            return

        self.show_notification(app_name, summary, body, emoji)

    def show_notification(self, app_name, summary, body, emoji):
        """Displays incoming notification in the dynamic island for 4 seconds."""
        if self.notif_timer_id is not None:
            GLib.source_remove(self.notif_timer_id)
            self.notif_timer_id = None
        if self.hud_timer_id is not None:
            GLib.source_remove(self.hud_timer_id)
            self.hud_timer_id = None

        self.notif_icon.set_label(emoji if emoji else "🔔")
        header = f"{app_name} • {summary}" if (app_name and summary) else (app_name or summary or _("Notification"))
        self.notif_title.set_label(header)
        self.notif_body.set_label(body if body else summary)

        self.state = "notification"
        self.capsule.set_visible(False)
        self.hud_box.set_visible(False)
        self.expanded_card.set_visible(False)
        self.notification_box.set_visible(True)
        GLib.idle_add(self.reposition)

        self.notif_timer_id = GLib.timeout_add(4000, self._on_notification_timeout)

    def _on_notification_timeout(self):
        self.notif_timer_id = None
        if self.state == "notification":
            self.state = "idle"
            self.notification_box.set_visible(False)
            self.capsule.set_visible(True)
            self._update_capsule_display()
        return False

    # ==========================================
    # Bluetooth & TWS Headphone Events
    # ==========================================
    def _on_bluetooth_event(self, name, is_connected, battery, emoji, path):
        """Callback when a Bluetooth device connects, disconnects, or updates battery."""
        if not config_manager.get("modules", "bluetooth_hud", True):
            return

        self._update_bluetooth_status()

        if self.state == "expanded":
            return

        if is_connected:
            if battery is not None:
                percent_str = f"{battery}%"
                fraction = max(0.0, min(1.0, battery / 100.0))
            else:
                percent_str = _("Connected")
                fraction = 1.0
            self.show_hud(emoji if emoji else "🎧", name, percent_str, fraction, "hud-bluetooth")
        else:
            self.show_hud(emoji if emoji else "🎧", name, _("Disconnected"), 0.0, "hud-danger")

    def _update_bluetooth_status(self):
        """Refreshes connected Bluetooth devices list in Control Center."""
        if not hasattr(self, 'bluetooth_monitor') or not self.bluetooth_monitor:
            return

        devices = self.bluetooth_monitor.get_connected_devices()
        while child := self.card_bt_box.get_first_child():
            self.card_bt_box.remove(child)

        if not devices:
            self.card_bt_box.set_visible(False)
            return

        for dev in devices:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.add_css_class("card-bt-row")

            icon_lbl = Gtk.Label(label=dev.get("emoji", "🎧"))
            icon_lbl.add_css_class("card-bt-icon")

            name_lbl = Gtk.Label(label=dev.get("name", "Device"))
            name_lbl.add_css_class("card-bt-name")
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_hexpand(True)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(22)

            bat = dev.get("battery")
            bat_str = f"🔋 {bat}%" if bat is not None else _("Connected")
            bat_lbl = Gtk.Label(label=bat_str)
            bat_lbl.add_css_class("card-bt-bat")
            bat_lbl.set_halign(Gtk.Align.END)

            row.append(icon_lbl)
            row.append(name_lbl)
            row.append(bat_lbl)
            self.card_bt_box.append(row)

        self.card_bt_box.set_visible(True)

    # ==========================================
    # Micro-Pill & Hover/Song Peek Mechanics
    # ==========================================
    def _on_capsule_enter(self, controller, x, y):
        """Expands micro capsule to full peek width on mouse hover."""
        if self._leave_timer_id is not None:
            GLib.source_remove(self._leave_timer_id)
            self._leave_timer_id = None

        if self.state == "idle" and not self.is_hovered:
            self.is_hovered = True
            self._update_capsule_display()

    def _on_capsule_leave(self, controller):
        """Collapses peek capsule back to micro when mouse leaves (with debounce)."""
        if self._leave_timer_id is not None:
            GLib.source_remove(self._leave_timer_id)
            self._leave_timer_id = None

        if self.state == "idle" and self.is_hovered:
            self._leave_timer_id = GLib.timeout_add(250, self._on_leave_timeout)

    def _on_leave_timeout(self):
        self._leave_timer_id = None
        if self.state == "idle" and self.is_hovered:
            self.is_hovered = False
            self._update_capsule_display()
        return False

    def _trigger_song_peek(self):
        """Temporarily blooms micro capsule to full peek width when a song changes."""
        if self.song_peek_timer_id is not None:
            GLib.source_remove(self.song_peek_timer_id)
            self.song_peek_timer_id = None

        self.is_peeked = True
        self._update_capsule_display()

        # Revert back to micro after 3.5 seconds
        self.song_peek_timer_id = GLib.timeout_add(3500, self._on_song_peek_timeout)

    def _on_song_peek_timeout(self):
        self.song_peek_timer_id = None
        self.is_peeked = False
        self._update_capsule_display()
        return False

    def _update_capsule_display(self):
        """Updates capsule internal widget visibility and geometry based on micro/peek state."""
        if self.state != "idle":
            return

        use_micro = config_manager.get("appearance", "compact_micro_pill", True)
        is_media_active = (self.media_playing or (self.mpris_monitor and bool(self.mpris_monitor.title))) and config_manager.get("modules", "media_player", True)

        if use_micro and not self.is_peeked and not self.is_hovered:
            # Micro mode: 115px unobtrusive capsule
            self.title_label.set_visible(False)
            self.pill_lyric_label.set_visible(False)
            self.pill_hw_box.set_visible(False)
            self.pill_micro_icon.set_visible(is_media_active)
            target_w = IslandDimensions.PILL_MICRO_WIDTH
        else:
            # Peek mode: 360px expanded capsule showing all info
            self.pill_micro_icon.set_visible(False)
            if is_media_active:
                self.title_label.set_visible(False)
                self.pill_lyric_label.set_visible(True)
                title = self.mpris_monitor.title if self.mpris_monitor else ""
                icon = "🎵" if self.media_playing else "⏸"
                self.pill_lyric_label.set_label(f"{icon} {title[:20]}")
            else:
                self.title_label.set_visible(True)
                self.pill_lyric_label.set_visible(False)
            self.pill_hw_box.set_visible(True)
            target_w = IslandDimensions.PILL_PEEK_WIDTH

        self.capsule.set_size_request(target_w, IslandDimensions.BAR_HEIGHT)
        GLib.idle_add(self.reposition)

    # ==========================================
    # Window Realize & Positioning
    # ==========================================
    def _on_realize(self, widget):
        GLib.idle_add(self._setup_x11_properties)

    def _setup_x11_properties(self):
        try:
            surface = self.get_surface()
            if not surface:
                return False

            self.xid = surface.get_xid()
            logging.info(f"X11 Surface realized with XID: {hex(self.xid)}")

            subprocess.run([
                'xprop', '-id', str(self.xid),
                '-f', '_NET_WM_WINDOW_TYPE', '32a',
                '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DOCK'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.run([
                'xprop', '-id', str(self.xid),
                '-f', '_NET_WM_STATE', '32a',
                '-set', '_NET_WM_STATE', '_NET_WM_STATE_ABOVE, _NET_WM_STATE_STICKY, _NET_WM_STATE_SKIP_TASKBAR, _NET_WM_STATE_SKIP_PAGER'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self._last_geometry = None
            self._update_capsule_display()
            return False
        except Exception as e:
            logging.error(f"Error configuring X11 window hints: {e}")
            return False

    def reposition(self):
        """Positions overlay precisely at center of selected display monitor."""
        if not self.xid:
            return

        display = Gdk.Display.get_default()
        if not display:
            return

        monitors = display.get_monitors()
        n_monitors = monitors.get_n_items()
        if n_monitors == 0:
            return

        target_idx = config_manager.get("appearance", "monitor_index", 0)
        if target_idx < 0 or target_idx >= n_monitors:
            target_idx = 0

        target_monitor = monitors.get_item(target_idx)
        geom = target_monitor.get_geometry()

        if self.state == "expanded":
            has_lyrics = config_manager.get("modules", "show_synced_lyrics", True)
            w = IslandDimensions.CARD_WIDTH
            is_media_active = (self.media_playing or (self.mpris_monitor and bool(self.mpris_monitor.title))) and config_manager.get("modules", "media_player", True)
            bt_extra = IslandDimensions.BT_ROW_HEIGHT if (hasattr(self, 'card_bt_box') and self.card_bt_box.get_visible()) else 0
            if is_media_active:
                h = (IslandDimensions.CARD_HEIGHT_FULL if has_lyrics else IslandDimensions.CARD_HEIGHT_MEDIA) + bt_extra
            else:
                h = IslandDimensions.CARD_HEIGHT_DASHBOARD + bt_extra
            self.expanded_card.set_size_request(w, h)
        elif self.state == "hud":
            w, h = IslandDimensions.HUD_WIDTH, IslandDimensions.BAR_HEIGHT
        elif self.state == "notification":
            w, h = IslandDimensions.NOTIFICATION_WIDTH, IslandDimensions.BAR_HEIGHT
        else:  # idle
            use_micro = config_manager.get("appearance", "compact_micro_pill", True)
            if use_micro and not self.is_peeked and not self.is_hovered:
                w, h = IslandDimensions.PILL_MICRO_WIDTH, IslandDimensions.BAR_HEIGHT
            else:
                w, h = IslandDimensions.PILL_PEEK_WIDTH, IslandDimensions.BAR_HEIGHT

        y_offset = config_manager.get("appearance", "y_offset", 8)
        center_x = geom.x + (geom.width - w) // 2
        pos_y = geom.y + y_offset

        target_geometry = (center_x, pos_y, w, h)
        if target_geometry == self._last_geometry:
            return
        self._last_geometry = target_geometry

        subprocess.run([
            'wmctrl', '-i', '-r', str(self.xid),
            '-e', f'0,{center_x},{pos_y},{w},{h}'
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def expand_card(self):
        """Expands island from compact capsule to interactive Control Center."""
        if self.hud_timer_id is not None:
            GLib.source_remove(self.hud_timer_id)
            self.hud_timer_id = None
        if self.notif_timer_id is not None:
            GLib.source_remove(self.notif_timer_id)
            self.notif_timer_id = None
        if self.song_peek_timer_id is not None:
            GLib.source_remove(self.song_peek_timer_id)
            self.song_peek_timer_id = None
        self.is_peeked = False

        self._update_bluetooth_status()
        has_lyrics = config_manager.get("modules", "show_synced_lyrics", True)
        is_media_active = (self.media_playing or (self.mpris_monitor and bool(self.mpris_monitor.title))) and config_manager.get("modules", "media_player", True)

        self.media_section.set_visible(is_media_active)
        self.karaoke_box.set_visible(is_media_active and has_lyrics)

        bt_extra = IslandDimensions.BT_ROW_HEIGHT if (hasattr(self, 'card_bt_box') and self.card_bt_box.get_visible()) else 0
        if is_media_active:
            target_h = (IslandDimensions.CARD_HEIGHT_FULL if has_lyrics else IslandDimensions.CARD_HEIGHT_MEDIA) + bt_extra
        else:
            target_h = IslandDimensions.CARD_HEIGHT_DASHBOARD + bt_extra

        self.expanded_card.set_size_request(IslandDimensions.CARD_WIDTH, target_h)

        self.state = "expanded"
        self.capsule.set_visible(False)
        self.hud_box.set_visible(False)
        self.notification_box.set_visible(False)
        self.expanded_card.set_visible(True)
        GLib.idle_add(self.reposition)

    def collapse_to_idle(self):
        """Collapses expanded card back to compact capsule."""
        self.state = "idle"
        self.is_hovered = False
        self.is_peeked = False
        if self._leave_timer_id is not None:
            GLib.source_remove(self._leave_timer_id)
            self._leave_timer_id = None
        self.expanded_card.set_visible(False)
        self.hud_box.set_visible(False)
        self.notification_box.set_visible(False)
        self.capsule.set_visible(True)
        self._update_capsule_display()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Collapses expanded card or notification when user presses Escape."""
        if keyval == Gdk.KEY_Escape:
            if self.state == "expanded":
                self.collapse_to_idle()
                return True
            elif self.state == "notification":
                self._on_notification_timeout()
                return True
        return False

    def _on_capsule_clicked(self, gesture, n_press, x, y):
        """Clicking the capsule expands the full Control Center."""
        self.expand_card()

    # ==========================================
    # Interactive Seekbar Callbacks
    # ==========================================
    def _on_seekbar_seek(self, gesture, n_press, x, y):
        self._is_seeking = False
        w = self.media_seekbar.get_width()
        if w > 0 and self.media_duration > 0:
            frac = min(1.0, max(0.0, x / w))
            target_sec = frac * self.media_duration
            self.media_seekbar.set_fraction(frac)
            self.media_time_lbl.set_label(f"{format_time(target_sec)} / {format_time(self.media_duration)}")
            self.mpris_monitor.set_position(target_sec)

    def _on_seekbar_drag(self, gesture, offset_x, offset_y):
        self._is_seeking = True
        start_x, _ = gesture.get_start_point()
        w = self.media_seekbar.get_width()
        if w > 0 and self.media_duration > 0:
            cur_x = start_x + offset_x
            frac = min(1.0, max(0.0, cur_x / w))
            target_sec = frac * self.media_duration
            self.media_seekbar.set_fraction(frac)
            self.media_time_lbl.set_label(f"{format_time(target_sec)} / {format_time(self.media_duration)}")

    def _on_seekbar_drag_end(self, gesture, offset_x, offset_y):
        self._is_seeking = False
        start_x, _ = gesture.get_start_point()
        w = self.media_seekbar.get_width()
        if w > 0 and self.media_duration > 0:
            cur_x = start_x + offset_x
            frac = min(1.0, max(0.0, cur_x / w))
            target_sec = frac * self.media_duration
            self.mpris_monitor.set_position(target_sec)

    # ==========================================
    # Dynamic Configuration Live Updates
    # ==========================================
    def on_config_updated(self, key: str, value):
        """Reacts dynamically to settings switches without restarting application."""
        logging.info(f"IslandWindow applying config update: {key} = {value}")
        if key == "module_media_player":
            self.media_section.set_visible(value)
            self._update_capsule_display()

        elif key == "module_show_synced_lyrics":
            self.karaoke_box.set_visible(value)
            if self.state == "expanded":
                self.reposition()
            if not value and self.mpris_monitor.title:
                icon = "🎵" if self.media_playing else "⏸"
                self.pill_lyric_label.set_label(f"{icon} {self.mpris_monitor.title[:20]}")
            elif value and self.media_playing and self.mpris_monitor.title:
                if not self.lyrics_engine.current_lyrics:
                    self.lyrics_engine.fetch_lyrics_async(
                        artist=self.mpris_monitor.artist,
                        title=self.mpris_monitor.title,
                        callback=self._on_lyrics_loaded
                    )
            self.reposition()

        elif key in ("module_volume_hud", "module_brightness_hud", "module_battery_charging", "module_bluetooth_hud"):
            if not value and self.state == "hud":
                self._on_hud_timeout()

        elif key in ("y_offset", "monitor_index"):
            self.reposition()

        elif key == "module_power_profile_switcher":
            self.power_row.set_visible(value)

        elif key == "module_system_notifications":
            if not value and self.state == "notification":
                self._on_notification_timeout()

        elif key == "compact_micro_pill":
            self._update_capsule_display()

        elif key == "language":
            if hasattr(self, 'btn_settings'):
                self.btn_settings.set_label("⚙️ " + _("Settings"))
            if hasattr(self, 'power_lbl'):
                self.power_lbl.set_label(_("Power Mode"))
            if hasattr(self, 'btn_power_saver'):
                self.btn_power_saver.set_label("🍃 " + _("Power Saver"))
                self.btn_power_balanced.set_label("⚖️ " + _("Balanced"))
                self.btn_power_perf.set_label("🚀 " + _("Performance"))
            if hasattr(self, 'battery_monitor'):
                self._on_battery_event(
                    self.battery_monitor.is_charging,
                    self.battery_monitor.percentage,
                    False,
                    False
                )

    def _update_clock(self):
        self.clock_label.set_label(time.strftime("%H:%M"))
        if hasattr(self, 'card_date_lbl'):
            self.card_date_lbl.set_label(time.strftime("%A, %d %b • %H:%M"))
        return True
