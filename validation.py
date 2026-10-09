import ipaddress


def validate_ip(ip_address):
    """Return True when the supplied value is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False
