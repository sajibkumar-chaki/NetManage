from validation import validate_ip


def test_valid_ipv4():
    assert validate_ip("192.168.1.1") is True


def test_valid_ipv6():
    assert validate_ip("2001:db8::1") is True


def test_invalid_ip():
    assert validate_ip("999.999.1.1") is False
