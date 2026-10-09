
import ipaddress


def validate_ip(ip_address):
    """Return True if the address is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(ip_address.strip())
        return True
    except (ValueError, AttributeError):
        return False


def get_ip_version(ip_address):
    """Return the IP version, or None if the address is invalid."""
    try:
        address = ipaddress.ip_address(ip_address.strip())
        return address.version
    except (ValueError, AttributeError):
        return None