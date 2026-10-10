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


def test_search_device_by_ip(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")
    manager.add_device("Router1", "192.168.1.1", "Router", "Sydney")

    results = manager.search_devices("192.168.1.1")

    assert len(results) == 1
    assert results[0]["hostname"] == "Router1"


def test_search_device_by_type(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")
    manager.add_device("Router1", "192.168.1.1", "Router", "Sydney")

    results = manager.search_devices("router")

    assert len(results) == 1


def test_search_device_by_location(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")
    manager.add_device("Router1", "192.168.1.1", "Router", "Sydney")

    results = manager.search_devices("sydney")

    assert len(results) == 1


def test_search_device_no_match(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")

    results = manager.search_devices("Unknown")

    assert results == []


def test_search_device_empty_term(tmp_path):
    manager = DeviceManager(tmp_path / "devices.json")

    results = manager.search_devices("   ")

    assert results == []