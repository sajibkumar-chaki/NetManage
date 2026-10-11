import csv

from report import generate_report, export_csv


def test_generate_report():
    devices = [
        {
            "id": 1,
            "hostname": "R1",
            "ip_address": "192.168.1.1",
            "device_type": "Router",
            "location": "Sydney",
        },
        {
            "id": 2,
            "hostname": "S1",
            "ip_address": "192.168.1.2",
            "device_type": "Switch",
            "location": "Sydney",
        },
    ]

    report = generate_report(devices)

    assert "Total devices: 2" in report
    assert "Routers: 1" in report
    assert "Switches: 1" in report



def test_generate_report_unknown_types():
    devices = [
        {"device_type": "Router"},
        {"device_type": "Firewall"},
        {"device_type": "Access Point"},
    ]

    report = generate_report(devices)

    assert "Total devices: 3" in report
    assert "Routers: 1" in report
    assert "Other: 2" in report


def test_generate_report_empty_list():
    report = generate_report([])

    assert "Total devices: 0" in report
    assert "Routers: 0" in report
    assert "Switches: 0" in report
    assert "Servers: 0" in report
    assert "Other: 0" in report


def test_generate_report_case_handling():
    devices = [
        {"device_type": "ROUTER"},
        {"device_type": " switch "},
        {"device_type": "SeRvEr"},
        {"device_type": "OTHER"},
    ]

    report = generate_report(devices)

    assert "Total devices: 4" in report
    assert "Routers: 1" in report
    assert "Switches: 1" in report
    assert "Servers: 1" in report
    assert "Other: 1" in report



def test_export_csv_empty_data(tmp_path):
    filename = tmp_path / "empty.csv"

    result = export_csv([], filename)

    assert result == str(filename)
    assert filename.exists()

    with filename.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        assert reader.fieldnames == [
            "id", "hostname", "ip_address",
            "device_type", "location"
        ]
        assert list(reader) == []


def test_export_csv_extra_fields(tmp_path):
    filename = tmp_path / "extra_fields.csv"

    devices = [
        {
            "id": 1,
            "hostname": "Router1",
            "ip_address": "192.168.1.1",
            "device_type": "Router",
            "location": "Sydney",
            "mac_address": "AA:BB:CC:DD:EE:FF",
        }
    ]

    export_csv(devices, filename)

    with filename.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["hostname"] == "Router1"
    assert rows[0]["ip_address"] == "192.168.1.1"
    assert "mac_address" not in rows[0]


def test_export_csv_invalid_records(tmp_path):
    filename = tmp_path / "invalid_records.csv"

    devices = [
        None,
        "Invalid Device",
        {"id": 2, "hostname": "Incomplete"},
        {
            "id": 1,
            "hostname": "ValidRouter",
            "ip_address": "192.168.1.1",
            "device_type": "Router",
            "location": "Sydney",
        },
        {
            "id": 3,
            "hostname": "NoLocation",
            "ip_address": "192.168.1.3",
            "device_type": "Switch",
            "location": None,
        },
    ]

    export_csv(devices, filename)

    with filename.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["hostname"] == "ValidRouter"
    assert rows[0]["id"] == "1"


def test_export_csv_data_integrity(tmp_path):
    filename = tmp_path / "network" / "devices.csv"

    devices = [
        {
            "id": 1,
            "hostname": "Router1",
            "ip_address": "192.168.1.1",
            "device_type": "Router",
            "location": "Sydney",
        },
        {
            "id": 2,
            "hostname": "Switch1",
            "ip_address": "192.168.1.2",
            "device_type": "Switch",
            "location": "Melbourne",
        },
    ]

    result = export_csv(devices, filename)

    assert result == str(filename)
    assert filename.exists()

    with filename.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    for original, exported in zip(devices, rows):
        for field in [
            "id", "hostname", "ip_address",
            "device_type", "location"
        ]:
            assert exported[field] == str(original[field])
