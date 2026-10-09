
try:
    from NetManage.validation import validate_ip, get_ip_version
except ModuleNotFoundError:
    from validation import validate_ip, get_ip_version


def test_valid_ipv4():
    assert validate_ip("192.168.1.1") is True


def test_invalid_ipv4():
    assert validate_ip("999.999.1.1") is False


def test_valid_ipv6():
    assert validate_ip("2001:db8::1") is True


def test_invalid_ip_text():
    assert validate_ip("hello") is False


def test_ip_with_spaces():
    assert validate_ip(" 192.168.1.1 ") is True


def test_ipv4_version():
    assert get_ip_version("192.168.1.1") == 4


def test_ipv6_version():
    assert get_ip_version("2001:db8::1") == 6


def test_invalid_ip_version():
    assert get_ip_version("hello") is None