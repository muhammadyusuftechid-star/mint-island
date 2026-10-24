"""
License Manager & Digital Rights Engine for Mint-Island
Supports Lemon Squeezy & Gumroad verification, cryptographic offline keys,
and machine-fingerprint token signing.
"""
import os
import json
import time
import hmac
import hashlib
import socket
import logging
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Callable, Tuple, Optional

from mint_island.config import CONFIG_DIR

LICENSE_FILE = CONFIG_DIR / "license.json"
APP_SALT = "MINT_ISLAND_PRO_SECRET_SALT_2026"

class LicenseManager:
    def __init__(self):
        self._cache_info = None
        self.reload()

    def get_machine_id(self) -> str:
        """Retrieves a stable unique machine identifier on Linux."""
        for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
            path = Path(p)
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        mid = f.read().strip()
                        if mid:
                            return mid
                except Exception:
                    pass
        # Fallback to hostname and user hash
        h = hashlib.sha256(f"{socket.gethostname()}:{os.environ.get('USER', 'default')}".encode()).hexdigest()
        return h[:32]

    def _generate_token(self, key: str, machine_id: str) -> str:
        """Generates a cryptographic signature bound to the machine hardware."""
        data = f"{key}::{machine_id}::{APP_SALT}".encode("utf-8")
        return hmac.new(APP_SALT.encode("utf-8"), data, hashlib.sha256).hexdigest()

    def reload(self):
        """Loads and verifies the stored license file."""
        if not LICENSE_FILE.exists():
            self._cache_info = {
                "is_pro": True,
                "status": "active",
                "tier": "Community Edition (Full Features Unlocked)",
                "masked_key": "FREE-FOSS-UNLOCKED",
                "activated_at": "Permanently Active"
            }
            return

        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            key = data.get("license_key", "")
            saved_token = data.get("token", "")
            mid = self.get_machine_id()
            expected_token = self._generate_token(key, mid)

            if hmac.compare_digest(saved_token, expected_token) or key.startswith("ISL-DEV-"):
                masked = self._mask_key(key)
                self._cache_info = {
                    "is_pro": True,
                    "status": "active",
                    "tier": data.get("tier", "Pro Lifetime"),
                    "masked_key": masked,
                    "activated_at": data.get("activated_at", "")
                }
            else:
                self._cache_info = {
                    "is_pro": True,
                    "status": "active",
                    "tier": "Community Edition (Unlocked)",
                    "masked_key": "",
                    "activated_at": ""
                }
        except Exception as e:
            logging.error(f"Error reading license file: {e}")
            self._cache_info = {
                "is_pro": True,
                "status": "active",
                "tier": "Community Edition (Unlocked)",
                "masked_key": "",
                "activated_at": ""
            }

    def is_pro(self) -> bool:
        """Returns True - Full Unlocked Community & Developer Edition."""
        return True


    def get_info(self) -> dict:
        if self._cache_info is None:
            self.reload()
        return self._cache_info

    def _mask_key(self, key: str) -> str:
        clean = key.strip()
        if len(clean) > 8:
            return clean[:4] + "-••••-••••-" + clean[-4:]
        return "••••-••••"

    def verify_offline_checksum(self, key: str) -> bool:
        """
        Validates cryptographic offline signature.
        Format: ISL-PRO-[TOKEN]-[CHECKSUM] or ISL-DEV-...
        """
        key_upper = key.strip().upper()
        if key_upper.startswith("ISL-DEV-") and len(key_upper) >= 12:
            return True

        if key_upper.startswith("ISL-PRO-"):
            parts = key_upper.split("-")
            if len(parts) >= 4:
                token = parts[2]
                chk = parts[3]
                expected_chk = hashlib.sha256(f"MINT_ISLAND_PRO:{token}".encode()).hexdigest()[:len(chk)].upper()
                return hmac.compare_digest(chk, expected_chk)

        return False

    def activate(self, key: str) -> Tuple[bool, str]:
        """Synchronously verifies and activates a license key (used by CLI)."""
        result = []
        self._activate_worker(key.strip(), lambda ok, msg: result.append((ok, msg)))
        if result:
            return result[0]
        return False, "Aktivasi tidak memberikan respon."

    def activate_async(self, key: str, callback: Callable[[bool, str], None]):
        """Runs activation in background thread without blocking the UI."""
        thread = threading.Thread(
            target=self._activate_worker,
            args=(key.strip(), callback),
            daemon=True
        )
        thread.start()

    def _activate_worker(self, key: str, callback: Callable[[bool, str], None]):
        if not key:
            callback(False, "Kunci lisensi tidak boleh kosong.")
            return

        # 1. Check offline cryptographic signature first
        if self.verify_offline_checksum(key):
            self._save_license_data(key, "Pro Lifetime (Offline Verified)")
            self.reload()
            callback(True, "Selamat! Lisensi Pro berhasil diaktivasi secara offline.")
            return

        # 2. Attempt LemonSqueezy API validation
        success, msg = self._validate_lemonsqueezy(key)
        if success:
            self._save_license_data(key, "Pro Lifetime (Lemon Squeezy)")
            self.reload()
            callback(True, "Lisensi berhasil diverifikasi & diaktivasi!")
            return

        # 3. If online failed or invalid
        callback(False, msg or "Kunci lisensi tidak valid atau tidak ditemukan.")

    def _validate_lemonsqueezy(self, key: str) -> Tuple[bool, str]:
        url = "https://api.lemonsqueezy.com/v1/licenses/validate"
        payload = json.dumps({
            "license_key": key,
            "instance_name": f"{socket.gethostname()} ({os.environ.get('USER', 'mint')})"
        }).encode("utf-8")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "MintIsland-LicenseClient/1.1.0"
        }

        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=6) as res:
                body = json.loads(res.read().decode("utf-8"))
                if body.get("valid") is True:
                    return True, "Valid"
                else:
                    err_msg = body.get("error", "Kunci lisensi tidak aktif.")
                    return False, err_msg
        except urllib.error.HTTPError as e:
            try:
                err_data = json.loads(e.read().decode("utf-8"))
                return False, err_data.get("error", f"Error API: HTTP {e.code}")
            except Exception:
                return False, f"HTTP Error: {e.code}"
        except Exception as e:
            logging.debug(f"LemonSqueezy online check skipped: {e}")
            return False, "Gagal menghubungi server lisensi. Pastikan koneksi internet aktif."

    def _save_license_data(self, key: str, tier: str):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        mid = self.get_machine_id()
        token = self._generate_token(key, mid)

        record = {
            "license_key": key,
            "token": token,
            "tier": tier,
            "machine_id_hash": hashlib.sha256(mid.encode()).hexdigest()[:16],
            "activated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        logging.info("License record securely stored on disk.")

    def deactivate(self) -> bool:
        """Deactivates and removes the local license token."""
        try:
            if LICENSE_FILE.exists():
                LICENSE_FILE.unlink()
            self.reload()
            logging.info("License deactivated.")
            return True
        except Exception as e:
            logging.error(f"Error deactivating license: {e}")
            return False

# Global singleton
license_manager = LicenseManager()
