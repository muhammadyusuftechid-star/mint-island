"""
Audio Volume & Mute Listener via pactl / PipeWire
Monitors sink volume changes and emits HUD signals.
"""
import re
import time
import subprocess
import threading
import logging
from gi.repository import GLib

class VolumeMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.current_volume = 50
        self.is_muted = False
        self.running = True
        self.proc = None
        self._get_initial_state()
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _get_initial_state(self):
        try:
            vol = self._query_volume()
            mute = self._query_mute()
            if vol is not None:
                self.current_volume = vol
            if mute is not None:
                self.is_muted = mute
            logging.info(f"VolumeMonitor initialized: {self.current_volume}% (Muted={self.is_muted})")
        except Exception as e:
            logging.error(f"Error querying initial volume: {e}")

    def _query_volume(self):
        res = subprocess.run(
            ['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
            capture_output=True, text=True, check=False
        )
        if res.returncode == 0:
            match = re.search(r'(\d+)%', res.stdout)
            if match:
                return int(match.group(1))
        return None

    def _query_mute(self):
        res = subprocess.run(
            ['pactl', 'get-sink-mute', '@DEFAULT_SINK@'],
            capture_output=True, text=True, check=False
        )
        if res.returncode == 0:
            return "yes" in res.stdout.lower()
        return None

    def _listen_loop(self):
        """Runs 'pactl subscribe' to react instantly to volume button presses."""
        while self.running:
            try:
                self.proc = subprocess.Popen(
                    ['pactl', 'subscribe'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1
                )
                for line in iter(self.proc.stdout.readline, ''):
                    if not self.running:
                        break
                    # Events on sink or server signify volume or mute adjustments
                    if "sink" in line.lower() or "server" in line.lower():
                        vol = self._query_volume()
                        mute = self._query_mute()
                        if vol is not None and mute is not None:
                            if vol != self.current_volume or mute != self.is_muted:
                                self.current_volume = vol
                                self.is_muted = mute
                                GLib.idle_add(self.callback, self.current_volume, self.is_muted)
            except Exception as e:
                logging.error(f"Volume listener error: {e}")
            
            # Throttle retry to prevent rapid CPU loop if pactl exits
            if self.running:
                time.sleep(1.0)

    def set_volume(self, volume: int):
        """Sets default sink volume to given percentage (0-100)."""
        vol = max(0, min(100, int(volume)))
        self.current_volume = vol
        subprocess.run(
            ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f"{vol}%"],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def toggle_mute(self):
        """Toggles mute on default sink."""
        self.is_muted = not self.is_muted
        subprocess.run(
            ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def stop(self):
        self.running = False
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass

