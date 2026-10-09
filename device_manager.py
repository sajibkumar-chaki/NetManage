import json
from pathlib import Path


class DeviceManager:
    """Manages network devices and persists them in a JSON file."""

    def __init__(self, data_file="data/devices.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.devices = self._load_devices()

    def _load_devices(self):
        if not self.data_file.exists():
            return []

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_devices(self):
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(self.devices, file, indent=4)

    def add_device(self, hostname, ip_address, device_type, location):
        # Prevent duplicate IP addresses
        for device in self.devices:
            if device["ip_address"] == ip_address:
                raise ValueError(
                    f"IP address {ip_address} is already registered."
                )

        next_id = max(
            (device["id"] for device in self.devices),
            default=0
        ) + 1

        device = {
            "id": next_id,
            "hostname": hostname,
            "ip_address": ip_address,
            "device_type": device_type,
            "location": location
        }

        self.devices.append(device)
        self._save_devices()
        return device

    def get_all_devices(self):
        return self.devices

    def get_device(self, device_id):
        for device in self.devices:
            if device["id"] == device_id:
                return device
        return None

    def search_devices(self, term):
        term = term.lower()

        return [
            device
            for device in self.devices
            if (
                term in device["hostname"].lower()
                or term in device["ip_address"].lower()
                or term in device["device_type"].lower()
                or term in device["location"].lower()
            )
        ]
    
    @staticmethod
    def search_device(devices, search_term):
        """Search devices by hostname, IP address, device type, or location."""
        search_term = search_term.strip().casefold()

        if not search_term:
            return []

        results = []

        for device in devices:
            searchable_fields = [
                str(device.get("hostname", "")),
                str(device.get("ip_address", "")),
                str(device.get("device_type", "")),
                str(device.get("location", "")),
            ]

            if any(search_term in field.casefold() for field in searchable_fields):
                results.append(device)

        return results
    
