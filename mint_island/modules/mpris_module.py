"""
MPRIS v2 Media Player Listener & Controller
Supports YouTube (Brave/Chrome/Firefox), Spotify, VLC, MPV via D-Bus.
"""
import dbus
import logging
from typing import Optional, Dict, Any
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class MPRISMonitor:
    def __init__(self, on_track_change_cb, on_position_tick_cb=None):
        self.on_track_change_cb = on_track_change_cb
        self.on_position_tick_cb = on_position_tick_cb

        self.bus = None
        self.active_player_name: Optional[str] = None
        self.active_player_obj = None
        self.player_iface = None
        self.props_iface = None

        self.status = "Stopped"
        self.title = ""
        self.artist = ""
        self.art_url = ""
        self.duration_sec = 0.0
        self.position_sec = 0.0

        self._prop_signal_match = None
        self.position_timer_id = None
        self._setup()

    def _setup(self):
        try:
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SessionBus()

            # Listen for new or terminating MPRIS players
            self.bus.add_signal_receiver(
                self._on_name_owner_changed,
                signal_name='NameOwnerChanged',
                dbus_interface='org.freedesktop.DBus'
            )

            # Discover currently running players
            self._discover_players()
        except Exception as e:
            logging.error(f"Error setting up MPRISMonitor: {e}")

    def _discover_players(self):
        """Finds active MPRIS players and attaches to the primary one."""
        try:
            players = [n for n in self.bus.list_names() if n.startswith("org.mpris.MediaPlayer2.")]
            if not players:
                self._set_inactive()
                return

            # Check if current player is still valid
            if self.active_player_name in players:
                self._inspect_player(self.active_player_name)
                return

            # Prefer player that is currently Playing
            chosen = players[0]
            for p in players:
                try:
                    obj = self.bus.get_object(p, '/org/mpris/MediaPlayer2')
                    props = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
                    status = str(props.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
                    if status == "Playing":
                        chosen = p
                        break
                except Exception:
                    pass

            self._attach_to_player(chosen)
        except Exception as e:
            logging.error(f"Error discovering MPRIS players: {e}")

    def _attach_to_player(self, player_name: str):
        try:
            # Remove previous signal receiver if existing
            if self._prop_signal_match:
                try:
                    self._prop_signal_match.remove()
                except Exception:
                    pass
                self._prop_signal_match = None

            self.active_player_name = player_name
            self.active_player_obj = self.bus.get_object(player_name, '/org/mpris/MediaPlayer2')
            self.player_iface = dbus.Interface(self.active_player_obj, 'org.mpris.MediaPlayer2.Player')
            self.props_iface = dbus.Interface(self.active_player_obj, 'org.freedesktop.DBus.Properties')

            # Listen for property changes from this player
            self._prop_signal_match = self.bus.add_signal_receiver(
                self._on_properties_changed,
                signal_name='PropertiesChanged',
                dbus_interface='org.freedesktop.DBus.Properties',
                bus_name=player_name,
                path='/org/mpris/MediaPlayer2'
            )

            self._inspect_player(player_name)
            logging.info(f"Attached to MPRIS player: {player_name}")
        except Exception as e:
            logging.error(f"Failed to attach to player {player_name}: {e}")
            self._set_inactive()

    def _inspect_player(self, player_name: str):
        try:
            status = str(self.props_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
            metadata = self.props_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
            self._update_track_info(status, metadata)
        except Exception as e:
            logging.debug(f"Error inspecting player {player_name}: {e}")

    def _update_track_info(self, status: str, metadata: Dict[str, Any]):
        self.status = status
        self.title = str(metadata.get('xesam:title', ''))
        self.track_id = str(metadata.get('mpris:trackid', ''))

        # Artist can be string or list
        artists = metadata.get('xesam:artist', [])
        if isinstance(artists, (list, dbus.Array)) and artists:
            self.artist = ", ".join(str(a) for a in artists)
        elif artists:
            self.artist = str(artists)
        else:
            self.artist = ""

        self.art_url = str(metadata.get('mpris:artUrl', ''))

        # Duration (in microseconds)
        length_us = metadata.get('mpris:length', 0)
        self.duration_sec = float(length_us) / 1_000_000.0 if length_us else 0.0

        # Read position
        self.position_sec = self.get_position()

        # Handle position tick timer
        if self.status == "Playing":
            self._start_position_timer()
        else:
            self._stop_position_timer()

        # Emit to GTK main thread
        GLib.idle_add(
            self.on_track_change_cb,
            self.status,
            self.title,
            self.artist,
            self.art_url,
            self.duration_sec,
            self.position_sec
        )

    def _on_properties_changed(self, interface, changed_props, invalidated_props):
        if interface != 'org.mpris.MediaPlayer2.Player':
            return

        status = str(changed_props.get('PlaybackStatus', self.status))
        metadata = changed_props.get('Metadata', None)
        if metadata is not None or status != self.status:
            if metadata is None:
                try:
                    metadata = self.props_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                except Exception:
                    metadata = {}
            self._update_track_info(status, metadata)

    def _on_name_owner_changed(self, name, old_owner, new_owner):
        if not name.startswith("org.mpris.MediaPlayer2."):
            return

        if not new_owner and name == self.active_player_name:
            # Current player was closed
            logging.info(f"Player closed: {name}")
            self._set_inactive()
            self._discover_players()
        elif new_owner and not old_owner:
            # New player opened
            logging.info(f"New player appeared: {name}")
            self._discover_players()

    def _set_inactive(self):
        if self._prop_signal_match:
            try:
                self._prop_signal_match.remove()
            except Exception:
                pass
            self._prop_signal_match = None

        self.active_player_name = None
        self.status = "Stopped"
        self.title = ""
        self.artist = ""
        self.art_url = ""
        self.track_id = ""
        self.duration_sec = 0.0
        self.position_sec = 0.0
        self._stop_position_timer()
        GLib.idle_add(
            self.on_track_change_cb,
            "Stopped", "", "", "", 0.0, 0.0
        )

    def get_position(self) -> float:
        """Queries current position in seconds."""
        if not self.props_iface or self.status == "Stopped":
            return 0.0
        try:
            pos_us = self.props_iface.Get('org.mpris.MediaPlayer2.Player', 'Position')
            self.position_sec = float(pos_us) / 1_000_000.0
            return self.position_sec
        except Exception:
            return self.position_sec

    def set_position(self, pos_sec: float):
        """Seeks to a specific position in seconds (interactive seekbar)."""
        if not self.active_player_name or not self.player_iface:
            return
        pos_us = int(max(0.0, pos_sec) * 1_000_000)
        track_id = getattr(self, 'track_id', '') or '/org/mpris/MediaPlayer2/TrackList/NoTrack'
        try:
            self.player_iface.SetPosition(track_id, dbus.Int64(pos_us))
            self.position_sec = pos_sec
            return
        except Exception:
            pass

        # Fallback to Seek with offset
        try:
            cur_pos = self.get_position()
            diff_us = int((pos_sec - cur_pos) * 1_000_000)
            self.player_iface.Seek(dbus.Int64(diff_us))
            self.position_sec = pos_sec
        except Exception as e:
            logging.debug(f"Seek failed: {e}")

    def _start_position_timer(self):
        """Starts 250ms interval timer for smooth karaoke lyrics sync."""
        if self.position_timer_id is None:
            self.position_timer_id = GLib.timeout_add(250, self._on_position_tick)

    def _stop_position_timer(self):
        if self.position_timer_id is not None:
            GLib.source_remove(self.position_timer_id)
            self.position_timer_id = None

    def _on_position_tick(self):
        if self.status != "Playing":
            self.position_timer_id = None
            return False

        try:
            pos = self.get_position()
            if self.on_position_tick_cb:
                self.on_position_tick_cb(pos)
        except Exception as e:
            logging.debug(f"Position tick callback error: {e}")

        return True

    # Playback Controls
    def play_pause(self):
        if not self.active_player_name or not self.player_iface:
            return
        try:
            self.player_iface.PlayPause()
        except dbus.DBusException as e:
            err = e.get_dbus_name()
            logging.debug(f"Player unavailable on PlayPause: {err}")
            if "ServiceUnknown" in err or "NameHasNoOwner" in err:
                self._set_inactive()
        except Exception as e:
            logging.debug(f"Error executing PlayPause: {e}")

    def next(self):
        """Skips to next track or jumps +10 seconds if next is not supported."""
        if not self.active_player_name or not self.player_iface:
            return
        try:
            self.player_iface.Next()
        except dbus.DBusException as e:
            err = e.get_dbus_name()
            logging.debug(f"Next not supported or unavailable: {err}")
            if "ServiceUnknown" in err or "NameHasNoOwner" in err:
                self._set_inactive()
            else:
                # Fallback: jump 10 seconds forward
                self.set_position(self.get_position() + 10.0)
        except Exception as e:
            logging.debug(f"Error executing Next: {e}")

    def previous(self):
        """Skips to previous track, restarts track, or jumps -10 seconds."""
        if not self.active_player_name or not self.player_iface:
            return
        try:
            self.player_iface.Previous()
        except dbus.DBusException as e:
            err = e.get_dbus_name()
            logging.debug(f"Previous not supported or unavailable: {err}")
            if "ServiceUnknown" in err or "NameHasNoOwner" in err:
                self._set_inactive()
            else:
                cur = self.get_position()
                if cur > 5.0:
                    self.set_position(0.0)
                else:
                    self.set_position(max(0.0, cur - 10.0))
        except Exception as e:
            logging.debug(f"Error executing Previous: {e}")


