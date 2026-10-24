"""
Synced Lyrics Engine (LRCLIB & Karaoke Timing)
Fetches and synchronizes lyrics in real-time from LRCLIB API.
"""
import re
import json
import time
import urllib.request
import urllib.parse
import threading
import logging
import os
from pathlib import Path
from typing import List, Tuple, Optional

# Persistent XDG Cache directory
XDG_CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
LYRICS_CACHE_DIR = XDG_CACHE / "mint-island" / "lyrics"

class LyricsEngine:
    def __init__(self):
        self._cache = {}
        self._inflight = set()
        self._failed_cache = {}
        self.current_lyrics: List[Tuple[float, str]] = []
        self.current_track_key: Optional[str] = None
        self.is_fetching = False

        # Ensure cache directory exists
        try:
            LYRICS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def clean_youtube_title(self, raw_title: str) -> Tuple[str, str]:
        """
        Cleans YouTube noise (e.g. 'Queen - Bohemian Rhapsody (Official Video) [4K]')
        and splits into (artist, title).
        """
        if not raw_title:
            return "", ""

        pattern = r'\s*[\(\[][^()\[\]]*(?:official|video|audio|remaster|lyric|mv|4k|hd|feat|ft\.|visualizer)[^()\[\]]*[\)\]]'
        cleaned = re.sub(pattern, '', raw_title, flags=re.IGNORECASE)
        cleaned = cleaned.strip(" -\"'")

        # Normalize unicode dashes (en-dash, em-dash) to standard ASCII separator
        cleaned = re.sub(r'\s*[\u2013\u2014]\s*', ' - ', cleaned)

        if " - " in cleaned:
            parts = cleaned.split(" - ", 1)
            return parts[0].strip(), parts[1].strip()

        return "", cleaned

    def fetch_lyrics_async(self, artist: str, title: str, callback=None):
        """Asynchronously fetches synced lyrics in a background thread."""
        thread = threading.Thread(
            target=self._fetch_worker,
            args=(artist, title, callback),
            daemon=True
        )
        thread.start()

    def _fetch_worker(self, artist: str, title: str, callback=None):
        clean_artist, clean_title = artist.strip(), title.strip()
        if not clean_artist and " - " in clean_title:
            clean_artist, clean_title = self.clean_youtube_title(clean_title)

        cache_key = f"{clean_artist.lower()}:::{clean_title.lower()}"
        if not cache_key.replace(":::", "").strip():
            if callback:
                callback([])
            return

        # Avoid redundant concurrent queries for identical track
        if cache_key in self._inflight:
            return

        # Throttle failed lookups for 30 seconds to prevent hammering API
        now = time.time()
        if cache_key in self._failed_cache and (now - self._failed_cache[cache_key]) < 30:
            if callback:
                callback([])
            return

        safe_filename = "".join(c for c in cache_key if c.isalnum() or c in (' ', '_', '-')).rstrip()
        cache_file = LYRICS_CACHE_DIR / f"{safe_filename[:120]}.json"

        # 1. Check in-memory cache
        if cache_key in self._cache:
            self.current_lyrics = self._cache[cache_key]
            self.current_track_key = cache_key
            if callback:
                callback(self.current_lyrics)
            return

        # 2. Check persistent disk cache (Works completely Offline!)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    disk_data = json.load(f)
                    self.current_lyrics = [(float(item[0]), str(item[1])) for item in disk_data]
                    self._cache[cache_key] = self.current_lyrics
                    self.current_track_key = cache_key
                    logging.info(f"Loaded lyrics from offline disk cache: {clean_title}")
                    if callback:
                        callback(self.current_lyrics)
                    return
            except Exception as e:
                logging.debug(f"Error reading disk cache: {e}")

        # 3. Fetch from LRCLIB API with in-flight tracking
        self._inflight.add(cache_key)
        try:
            lyrics_list = self._fetch_from_lrclib(clean_artist, clean_title, cache_key)
        finally:
            self._inflight.discard(cache_key)

        # Save to in-memory and disk cache
        if len(self._cache) >= 100:
            for k in list(self._cache.keys())[:20]:
                self._cache.pop(k, None)

        self._cache[cache_key] = lyrics_list
        self.current_lyrics = lyrics_list
        self.current_track_key = cache_key

        if lyrics_list:
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(lyrics_list, f)
            except Exception as e:
                logging.debug(f"Error saving disk cache: {e}")

        if callback:
            callback(self.current_lyrics)

    def _fetch_from_lrclib(self, artist: str, title: str, cache_key: str = "") -> List[Tuple[float, str]]:
        headers = {"User-Agent": "MintIsland/0.3.0 (Linux Mint Dynamic Island)"}

        # 1. Try exact get if artist is known
        if artist and title:
            try:
                url = "https://lrclib.net/api/get?" + urllib.parse.urlencode({
                    "artist_name": artist,
                    "track_name": title
                })
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=4) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    synced = data.get("syncedLyrics")
                    if synced:
                        return self.parse_lrc(synced)
            except urllib.error.HTTPError as e:
                if e.code == 503:
                    logging.warning("LRCLIB service is temporarily unavailable (503). Using offline fallback.")
                else:
                    logging.debug(f"LRCLIB HTTP error: {e.code}")
                if cache_key:
                    self._failed_cache[cache_key] = time.time()
            except Exception as e:
                logging.debug(f"LRCLIB exact match not found: {e}")
                if cache_key:
                    self._failed_cache[cache_key] = time.time()

        # 2. Try general search with query
        query = f"{artist} {title}".strip()
        if not query:
            return []

        try:
            url = "https://lrclib.net/api/search?" + urllib.parse.urlencode({"q": query})
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as res:
                results = json.loads(res.read().decode("utf-8"))
                for item in results:
                    synced = item.get("syncedLyrics")
                    if synced:
                        return self.parse_lrc(synced)
                    # Fallback to plainLyrics if no synced
                    plain = item.get("plainLyrics")
                    if plain:
                        # Convert plain to single lines without timestamps
                        lines = [line.strip() for line in plain.split("\n") if line.strip()]
                        return [(i * 3.0, line) for i, line in enumerate(lines)]
        except urllib.error.HTTPError as e:
            if e.code == 503:
                logging.warning("LRCLIB search API is temporarily unavailable (503).")
            else:
                logging.debug(f"LRCLIB search HTTP error: {e.code}")
            if cache_key:
                self._failed_cache[cache_key] = time.time()
        except Exception as e:
            logging.debug(f"LRCLIB search error: {e}")
            if cache_key:
                self._failed_cache[cache_key] = time.time()

        return []

    def parse_lrc(self, lrc_text: str) -> List[Tuple[float, str]]:
        """Parses [mm:ss.xx] lines into a list of (timestamp_sec, text)."""
        parsed = []
        pattern = re.compile(r'\[(\d+):(\d{2}(?:\.\d+)?)\](.*)')
        for line in lrc_text.splitlines():
            line = line.strip()
            match = pattern.match(line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3).strip()
                timestamp = minutes * 60 + seconds
                parsed.append((timestamp, text))

        parsed.sort(key=lambda x: x[0])
        return parsed

    def get_current_lyric(self, pos_sec: float) -> Tuple[int, str, str]:
        """
        Returns (index, current_line, next_line) for the current playback timestamp.
        """
        if not self.current_lyrics:
            return -1, "", ""

        active_idx = -1
        for i, (ts, text) in enumerate(self.current_lyrics):
            if pos_sec >= ts:
                active_idx = i
            else:
                break

        if active_idx == -1:
            return -1, "...", self.current_lyrics[0][1] if self.current_lyrics else ""

        current_text = self.current_lyrics[active_idx][1]
        next_text = self.current_lyrics[active_idx + 1][1] if (active_idx + 1 < len(self.current_lyrics)) else ""
        return active_idx, current_text, next_text

    def clear(self):
        """Clears active lyrics from RAM when media stops to maintain <45MB RSS."""
        self.current_lyrics = []
        self.current_track_key = None

