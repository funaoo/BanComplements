import json
import time
from pathlib import Path
from threading import Lock

from endstone_ban_complements.timeutil import now_stamp


class Storage:
    def __init__(self, data_folder: str) -> None:
        self._path = Path(data_folder) / "data.json"
        self._lock = Lock()
        self._data = {"bans": {}, "ip_bans": {}, "mutes": {}, "players": {}}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with self._path.open("r", encoding="utf-8") as file:
                self._data.update(json.load(file))

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file, indent=2)

    def register_player(self, name: str, address: str) -> None:
        with self._lock:
            self._data["players"][name] = {"address": address}
            self._save()

    def get_player_address(self, name: str) -> str | None:
        entry = self._data["players"].get(name)
        return entry["address"] if entry else None

    def is_banned(self, name: str) -> dict | None:
        return self._get_active(self._data["bans"], name)

    def ban(self, name: str, staff: str, reason: str, expires_at: float | None) -> None:
        with self._lock:
            self._data["bans"][name] = {
                "staff": staff,
                "reason": reason,
                "date": now_stamp(),
                "expires_at": expires_at,
            }
            self._save()

    def unban(self, name: str) -> bool:
        return self._remove(self._data["bans"], name)

    def is_ip_banned(self, ip: str) -> dict | None:
        return self._get_active(self._data["ip_bans"], ip)

    def ban_ip(self, ip: str, owner: str, staff: str, reason: str, expires_at: float | None) -> None:
        with self._lock:
            self._data["ip_bans"][ip] = {
                "owner": owner,
                "staff": staff,
                "reason": reason,
                "date": now_stamp(),
                "expires_at": expires_at,
            }
            self._save()

    def unban_ip(self, ip: str) -> bool:
        return self._remove(self._data["ip_bans"], ip)

    def is_muted(self, name: str) -> dict | None:
        return self._get_active(self._data["mutes"], name)

    def mute(self, name: str, staff: str, reason: str, expires_at: float) -> None:
        with self._lock:
            self._data["mutes"][name] = {
                "staff": staff,
                "reason": reason,
                "date": now_stamp(),
                "expires_at": expires_at,
            }
            self._save()

    def unmute(self, name: str) -> bool:
        return self._remove(self._data["mutes"], name)

    def all_bans(self) -> dict:
        return dict(self._data["bans"])

    def all_ip_bans(self) -> dict:
        return dict(self._data["ip_bans"])

    def all_mutes(self) -> dict:
        return dict(self._data["mutes"])

    def purge_expired(self) -> None:
        with self._lock:
            changed = False
            for bucket in ("bans", "ip_bans", "mutes"):
                expired = [
                    key
                    for key, entry in self._data[bucket].items()
                    if entry["expires_at"] is not None and entry["expires_at"] <= time.time()
                ]
                for key in expired:
                    del self._data[bucket][key]
                    changed = True
            if changed:
                self._save()

    def _get_active(self, bucket: dict, key: str) -> dict | None:
        entry = bucket.get(key)
        if entry is None:
            return None
        if entry["expires_at"] is not None and entry["expires_at"] <= time.time():
            self._remove(bucket, key)
            return None
        return entry

    def _remove(self, bucket: dict, key: str) -> bool:
        with self._lock:
            if key not in bucket:
                return False
            del bucket[key]
            self._save()
            return True
