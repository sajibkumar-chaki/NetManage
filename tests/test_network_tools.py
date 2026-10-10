
from subprocess import TimeoutExpired
from unittest.mock import patch

from network_tools import check_connectivity, get_diagnostics


def test_invalid_ip():
    assert check_connectivity("999.999.1.1") == "Invalid IP Address"


def test_invalid_timeout():
    assert check_connectivity("127.0.0.1", timeout=0) == "Invalid Timeout"


@patch("network_tools.subprocess.run")
def test_reachable_device(mock_run):
    mock_run.return_value.returncode = 0

    assert check_connectivity("127.0.0.1") == "Reachable"


@patch("network_tools.subprocess.run")
def test_no_ping_response(mock_run):
    mock_run.return_value.returncode = 1

    assert check_connectivity("192.0.2.1") == "No Ping Response"


@patch("network_tools.subprocess.run")
def test_ping_timeout(mock_run):
    mock_run.side_effect = TimeoutExpired(
        cmd="ping",
        timeout=2,
    )

    assert check_connectivity("127.0.0.1") == "Timeout"


@patch("network_tools.check_connectivity")
def test_diagnostics(mock_check):
    mock_check.return_value = "Reachable"

    device = {
        "hostname": "TestRouter1",
        "ip_address": "127.0.0.1",
        "device_type": "Router",
        "location": "Sydney",
    }

    result = get_diagnostics(device)

    assert result["Hostname"] == "TestRouter1"
    assert result["IP Address"] == "127.0.0.1"
    assert result["Device Type"] == "Router"
    assert result["Location"] == "Sydney"
    assert result["Connectivity"] == "Reachable"
