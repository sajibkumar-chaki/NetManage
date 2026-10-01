import csv
from collections import Counter
from pathlib import Path


def generate_report(devices):
    total = len(devices)

    type_counts = Counter(device["device_type"].lower() for device in devices)

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
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = ["id", "hostname", "ip_address", "device_type", "location"]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(devices)

    return str(path)
