
import csv
from collections import Counter
from pathlib import Path


def generate_report(devices):
    total = len(devices)

    type_counts = Counter()

    for device in devices:
        device_type = str(
            device.get("device_type", "")
        ).strip().lower()

        if device_type not in ("router", "switch", "server"):
            device_type = "other"

        type_counts[device_type] += 1

    return (
        "===== NETWORK REPORT =====\n\n"
        f"Total devices: {total}\n"
        f"Routers: {type_counts.get('router', 0)}\n"
        f"Switches: {type_counts.get('switch', 0)}\n"
        f"Servers: {type_counts.get('server', 0)}\n"
        f"Other: {type_counts.get('other', 0)}"
    )



def export_csv(devices, filename="data/devices.csv"):
    path = Path(filename)

    fields = [
        "id",
        "hostname",
        "ip_address",
        "device_type",
        "location",
    ]

    valid_devices = []

    for device in devices:
        # Skip records that are not dictionaries
        if not isinstance(device, dict):
            continue

        # Skip records with missing or None fields
        if any(
            field not in device or device[field] is None
            for field in fields
        ):
            continue

        # Keep only the expected CSV fields
        clean_device = {
            field: device[field]
            for field in fields
        }

        valid_devices.append(clean_device)

    # Create the output directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write valid device records to CSV
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(valid_devices)

    return str(path)

