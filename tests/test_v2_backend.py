import json
import threading
from unittest.mock import patch
import pytest
from device_manager import DeviceManager, file_lock
from monitoring import MonitorSession, validate_schedule
from network_tools import check_connectivity


@pytest.fixture
def manager(tmp_path):
    m = DeviceManager(tmp_path / "devices.json")
    m.add_device("Demo router", "2001:db8::1", "Router", "Sample lab")
    m.add_device("Demo switch", "192.0.2.2", "Switch", "Sample lab")
    return m


def test_edit_persistence_unchanged_and_canonical_duplicate(manager):
    assert manager.edit_device(1)["ip_address"] == "2001:db8::1"
    with pytest.raises(ValueError, match="already registered"):
        manager.edit_device(2, ip_address="2001:0db8:0:0:0:0:0:1")
    with pytest.raises(ValueError, match="already registered"):
        manager.add_device("Other", "2001:0db8::1", "Other", "Lab")
    manager.edit_device(1, hostname="Changed")
    assert DeviceManager(manager.data_file).get_device(1)["hostname"] == "Changed"


@pytest.mark.parametrize("changes", [{"hostname": ""}, {"ip_address":"bad"}, {"location":None}, {"device_type":"\n"}, {"id":4}])
def test_invalid_edit_leaves_file(manager, changes):
    before = manager.data_file.read_bytes()
    with pytest.raises(ValueError):
        manager.edit_device(1, **changes)
    assert manager.data_file.read_bytes() == before


def test_delete_confirmation_and_ids(manager):
    before = manager.data_file.read_bytes()
    assert not manager.delete_device(1)
    assert not manager.delete_device(1, "yes")
    assert manager.data_file.read_bytes() == before
    assert manager.delete_device(1, True)
    assert [d["id"] for d in DeviceManager(manager.data_file).get_all_devices()] == [2]
    with pytest.raises(ValueError): manager.delete_device(999, True)
    with pytest.raises(ValueError): manager.edit_device(999, hostname="Missing")


@pytest.mark.parametrize("content", ["{", "{}", '[{"id":1}]', '[null]'])
def test_corrupt_inventory_preserved(tmp_path, content):
    path = tmp_path / "devices.json"
    path.write_text(content)
    with pytest.raises(ValueError): DeviceManager(path)
    assert path.read_text() == content


def test_failed_atomic_save_rolls_back(manager):
    before = manager.data_file.read_bytes()
    with patch("device_manager.os.replace", side_effect=OSError("disk unavailable")):
        with pytest.raises(OSError): manager.delete_device(1, True)
    assert manager.data_file.read_bytes() == before
    assert len(manager.devices) == 2
    assert not list(manager.data_file.parent.glob(".inventory-*.tmp"))


def test_multiple_managers_do_not_lose_updates(manager):
    other = DeviceManager(manager.data_file)
    manager.edit_device(1, hostname="Updated")
    other.edit_device(2, location="New lab")
    assert other.get_device(1)["hostname"] == "Updated"
    with file_lock(manager.lock_path):
        with pytest.raises(ValueError, match="busy"): other.delete_device(2, True)


@pytest.mark.parametrize("interval,count", [(True,5),(float("nan"),5),(float("inf"),5),(0,5),(-1,5),(3601,5),(1,True),(1,2.5),(1,0),(1,1001)])
def test_schedule_limits(interval, count):
    with pytest.raises(ValueError): validate_schedule(interval,count)


def test_monitor_transitions_history_snapshot_and_lock(manager):
    results = iter(["Reachable", "No Ping Response", "Timeout", "Reachable", "Ping Error"])
    session = MonitorSession(manager,1,interval=.001,count=5,probe=lambda ip:next(results))
    rows=[]
    def receive(row):
        with pytest.raises(ValueError, match="busy"): manager.edit_device(1,hostname="Blocked")
        rows.append(row)
    session.run(receive)
    assert [r["event"] for r in rows] == ["Observation","Non-response observed","Observation","Recovery observed","Operational error"]
    manager.edit_device(1,hostname="Later")
    saved=[json.loads(line) for line in session.history_file.read_text().splitlines()]
    assert saved == rows and saved[0]["hostname"] == "Demo router"
    assert "+" in saved[0]["timestamp"] or saved[0]["timestamp"].endswith("Z")
    MonitorSession(manager,1,count=1,probe=lambda ip:"Timeout").run()
    assert len(session.history_file.read_text().splitlines()) == 6


def test_stop_interrupts_interval_and_releases_lock(manager):
    got=threading.Event()
    session=MonitorSession(manager,1,interval=3600,count=5,probe=lambda ip:"Reachable")
    worker=threading.Thread(target=lambda:session.run(lambda row:got.set()))
    worker.start()
    assert got.wait(2)
    session.stop()
    worker.join(2)
    assert not worker.is_alive()
    manager.delete_device(1,True)


def test_history_failure_not_reported_as_saved(manager,tmp_path):
    invalid=tmp_path / "directory"
    invalid.mkdir()
    rows=[]
    session=MonitorSession(manager,1,history_file=invalid,count=1,probe=lambda ip:"Reachable")
    with pytest.raises(OSError): session.run(rows.append)
    assert rows == []


def test_windows_unreachable_zero_exit():
    with patch("network_tools.sys.platform","win32"), patch("network_tools.subprocess.run") as run:
        run.return_value.returncode=0
        run.return_value.stdout="Reply from 192.0.2.1: Destination host unreachable."
        assert check_connectivity("192.0.2.2") == "No Ping Response"
        run.return_value.stdout="Reply from 127.0.0.1: bytes=32 time<1ms TTL=128"
        assert check_connectivity("127.0.0.1") == "Reachable"
        assert run.call_args.kwargs["timeout"] == 4
        assert isinstance(run.call_args.args[0],list)


def test_cli_cancel_preserves_inventory(manager,monkeypatch,capsys):
    from app import edit_device_menu,delete_device_menu
    before=manager.data_file.read_bytes()
    answers=iter(["1","/cancel"])
    monkeypatch.setattr("builtins.input",lambda prompt:next(answers))
    edit_device_menu(manager)
    answers=iter(["1","no"])
    delete_device_menu(manager)
    assert manager.data_file.read_bytes() == before
    assert "cancelled" in capsys.readouterr().out


def test_operational_ping_failure_distinct():
    with patch("network_tools.subprocess.run") as run:
        run.return_value.returncode=1
        run.return_value.stdout="Unable to contact IP driver. General failure."
        assert check_connectivity("127.0.0.1")=="Ping Error"


def test_monitor_missing_device_and_pre_cancel(manager):
    with pytest.raises(ValueError,match="not found"):
        MonitorSession(manager,99,count=1,probe=lambda ip:"Reachable").run()
    session=MonitorSession(manager,1,count=1,probe=lambda ip:pytest.fail("Cancelled probe ran"))
    session.stop()
    session.run()


def test_import_backup_and_source_preserved(tmp_path):
    source=DeviceManager(tmp_path/"source.json")
    source.add_device("Demo","127.0.0.1","Server","Lab")
    before=source.data_file.read_bytes()
    dest=DeviceManager(tmp_path/"destination.json")
    dest.data_file.write_text("[]")
    assert dest.import_inventory(source.data_file)==1
    assert source.data_file.read_bytes()==before
    backups=list(tmp_path.glob("devices.backup-*.json"))
    assert len(backups)==1 and backups[0].read_text()=="[]"


def test_stale_edit_rejected_under_transaction_lock(manager):
    other = DeviceManager(manager.data_file)
    original = manager.get_device(1)
    other.edit_device(1, location="New confirmed location")
    stale_fields = {key: original[key] for key in ("hostname", "ip_address", "device_type", "location")}
    stale_fields["hostname"] = "Stale editor rename"
    before = manager.data_file.read_bytes()
    with pytest.raises(ValueError, match="Refresh and reopen"):
        manager.edit_device(1, expected_device=original, **stale_fields)
    assert manager.data_file.read_bytes() == before
    assert manager.get_device(1)["location"] == "New confirmed location"
    assert manager.get_device(1)["hostname"] == original["hostname"]
    fresh = manager.get_device(1)
    manager.edit_device(1, expected_device=fresh, hostname="Fresh editor rename")
    assert other.get_device(1)["location"] == "New confirmed location"
    assert other.get_device(1)["hostname"] == "Fresh editor rename"


def test_stale_delete_confirmation_rejected(manager):
    original = manager.get_device(1)
    DeviceManager(manager.data_file).edit_device(1, location="Changed after confirmation opened")
    before = manager.data_file.read_bytes()
    with pytest.raises(ValueError, match="Device changed"):
        manager.delete_device(1, True, expected_device=original)
    assert manager.data_file.read_bytes() == before
    assert manager.get_device(1) is not None
    fresh = manager.get_device(1)
    assert manager.delete_device(1, True, expected_device=fresh)
    assert manager.get_device(1) is None
