
from device_manager import DeviceManager


devices = [
    {
        "hostname": "Router1",
        "ip_address": "192.168.1.1",
        "device_type": "Router",
        "location": "Sydney",
    },
    {
        "hostname": "Switch1",
        "ip_address": "192.168.1.2",
        "device_type": "Switch",
        "location": "Sydney",
    },
    {
        "hostname": "Server1",
        "ip_address": "10.0.0.10",
        "device_type": "Server",
        "location": "Melbourne",
    },
]

print(DeviceManager.search_device(devices, "router"))
print(DeviceManager.search_device(devices, "192.168.1.2"))
print(DeviceManager.search_device(devices, "Server"))
print(DeviceManager.search_device(devices, "unknown"))