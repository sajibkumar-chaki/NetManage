from device_manager import DeviceManager


DEVICES = [
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
]


def test_search_by_hostname():
    result = DeviceManager.search_device(DEVICES, "Router1")
    assert len(result) == 1
    assert result[0]["hostname"] == "Router1"


def test_search_by_ip():
    result = DeviceManager.search_device(DEVICES, "192.168.1.2")
    assert result[0]["hostname"] == "Switch1"


def test_search_by_device_type():
    result = DeviceManager.search_device(DEVICES, "router")
    assert len(result) == 1


def test_search_no_match():
    assert DeviceManager.search_device(DEVICES, "Unknown") == []


def test_search_empty_term():
    assert DeviceManager.search_device(DEVICES, "   ") == []
