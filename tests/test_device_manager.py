from device_manager import DeviceManager


def test_add_and_get_device(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")

    device = manager.add_device(
        "Router1", "192.168.1.1", "Router", "Sydney"
    )

    assert device["id"] == 1
    assert manager.get_device(1)["hostname"] == "Router1"


def test_search_device(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")

    manager.add_device("Router1", "192.168.1.1", "Router", "Sydney")
    manager.add_device("Switch1", "192.168.1.2", "Switch", "Melbourne")

    results = manager.search_devices("router")

    assert len(results) == 1
    assert results[0]["hostname"] == "Router1"
