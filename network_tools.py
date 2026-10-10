
import ipaddress
import platform
import subprocess


def check_connectivity(ip_address, timeout=2):
    """Check IPv4/IPv6 connectivity using the system ping command."""

    try:
        ip = ipaddress.ip_address(ip_address)
    except ValueError:
        return "Invalid IP Address"

    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0 < timeout < float("inf")
    ):
        return "Invalid Timeout"

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-6" if ip.version == 6 else "-4",
            "-n", "1",
            "-w", str(max(1, int(timeout * 1000))),
            str(ip),
        ]
    else:
        command = [
            "ping",
            "-6" if ip.version == 6 else "-4",
            "-c", "1",
            str(ip),
        ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
            check=False,
        )

        if result.returncode == 0:
            return "Reachable"

        return "No Ping Response"

    except subprocess.TimeoutExpired:
        return "Timeout"

    except (subprocess.SubprocessError, OSError):
        return "Ping Error"


def get_diagnostics(device):
    """Return basic device information and ping connectivity."""

    status = check_connectivity(device["ip_address"])

    return {
        "Hostname": device["hostname"],
        "IP Address": device["ip_address"],
        "Device Type": device["device_type"],
        "Location": device["location"],
        "Connectivity": status,
    }
