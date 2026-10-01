from report import generate_report


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
