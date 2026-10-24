"""Shared inventory service: atomic saves and OS-released interprocess locks."""
import copy
import ipaddress
import json
import os
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_lock(path):
    """Nonblocking lock; lock files persist, OS releases locks on process exit."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("Store is busy: another writer or monitoring session is active.") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def validate_fields(hostname, ip_address, device_type, location):
    values = [hostname, ip_address, device_type, location]
    if any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError("All fields must contain text.")
    if any(len(v) > 255 or any(ord(c) < 32 for c in v) for v in values):
        raise ValueError("Fields must be at most 255 characters without control characters.")
    hostname, ip_address, device_type, location = [v.strip() for v in values]
    ip_address = str(ipaddress.ip_address(ip_address))
    return dict(hostname=hostname, ip_address=ip_address, device_type=device_type, location=location)


class DeviceManager:
    """CLI default remains data/devices.json; desktop passes an explicit store."""
    def __init__(self, data_file="data/devices.json"):
        self.data_file = Path(data_file).resolve()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.data_file.with_suffix(".lock")
        self.monitor_lock = self.data_file.with_suffix(".monitor.lock")
        self.devices = self._load_devices()

    def _load_devices(self):
        if not self.data_file.exists():
            return []
        try:
            records = json.loads(self.data_file.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ValueError(f"Cannot read inventory {self.data_file}: {exc}. File preserved.") from exc
        if not isinstance(records, list):
            raise ValueError("Inventory must be a JSON list. File preserved.")
        ids, addresses = set(), set()
        for record in records:
            try:
                ident = record["id"]
                if type(ident) is not int or ident < 1 or ident in ids:
                    raise ValueError("invalid or duplicate ID")
                ids.add(ident)
                fields = validate_fields(*(record[k] for k in ("hostname", "ip_address", "device_type", "location")))
                address = fields["ip_address"]
                if address in addresses:
                    warnings.warn(f"Existing duplicate address {address}; resolve by editing or deleting.", RuntimeWarning)
                addresses.add(address)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid inventory record: {exc}. File preserved; repair a backup manually.") from exc
        return records

    def _save_devices(self):
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.data_file.parent,
                                             prefix=".inventory-", suffix=".tmp", delete=False) as handle:
                name = handle.name
                json.dump(self.devices, handle, indent=4)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, self.data_file)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)

    @contextmanager
    def _transaction(self):
        with file_lock(self.monitor_lock), file_lock(self.lock_path):
            self.devices = self._load_devices()
            previous = copy.deepcopy(self.devices)
            try:
                yield
                self._save_devices()
            except BaseException:
                self.devices = previous
                raise

    def _unique(self, address, own_id=None):
        for device in self.devices:
            if device["id"] != own_id and str(ipaddress.ip_address(device["ip_address"].strip())) == address:
                raise ValueError(f"IP address {address} is already registered.")

    def add_device(self, hostname, ip_address, device_type, location):
        fields = validate_fields(hostname, ip_address, device_type, location)
        with self._transaction():
            self._unique(fields["ip_address"])
            device = dict(id=max((d["id"] for d in self.devices), default=0) + 1, **fields)
            self.devices.append(device)
        return copy.deepcopy(device)

    def edit_device(self, device_id, **changes):
        if set(changes) - {"hostname", "ip_address", "device_type", "location"}:
            raise ValueError("Unknown device field.")
        with self._transaction():
            device = next((d for d in self.devices if d["id"] == device_id), None)
            if device is None or type(device_id) is not int:
                raise ValueError("Device not found.")
            fields = validate_fields(*(changes.get(k, device[k]) for k in ("hostname", "ip_address", "device_type", "location")))
            self._unique(fields["ip_address"], device_id)
            if fields["ip_address"] != str(ipaddress.ip_address(device["ip_address"])):
                for key in ("status", "last_checked", "connectivity"):
                    device.pop(key, None)
            device.update(fields)
        return copy.deepcopy(device)

    def delete_device(self, device_id, confirmed=False):
        if confirmed is not True:
            return False
        with self._transaction():
            if type(device_id) is not int or not any(d["id"] == device_id for d in self.devices):
                raise ValueError("Device not found.")
            self.devices = [d for d in self.devices if d["id"] != device_id]
        return True

    def get_all_devices(self):
        self.devices = self._load_devices()
        return copy.deepcopy(self.devices)

    def get_device(self, device_id):
        return next((d for d in self.get_all_devices() if type(device_id) is int and d["id"] == device_id), None)

    def search_devices(self, term):
        return self.search_device(self.get_all_devices(), term)

    @staticmethod
    def search_device(devices, search_term):
        term = search_term.strip().casefold()
        if not term:
            return []
        return [copy.deepcopy(d) for d in devices if any(term in str(d.get(k, "")).casefold()
                for k in ("hostname", "ip_address", "device_type", "location"))]
