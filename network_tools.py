
import ipaddress
import sys
import re
import subprocess


def check_connectivity(ip_address, timeout=2):
    """Check IPv4/IPv6 connectivity using the system ping command."""

    try:
        ip = ipaddress.ip_address(ip_address)
    except (ValueError, TypeError):
        return "Invalid IP Address"

    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0 < timeout < float("inf")
    ):
        return "Invalid Timeout"

    system = "windows" if sys.platform == "win32" else sys.platform

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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout + 2,
            check=False,
        )

        if result.returncode == 0:
            # Windows may return zero for an ICMP destination-unreachable error.
            # Require a reply measurement, independent of localized reply labels.
            output = result.stdout
            if system == "windows" and isinstance(output, str):
                if not re.search(r"(?:[=<]\s*\d+\s*ms\b|TTL[=：]\d+)", output, re.I):
                    return "No Ping Response"
            return "Reachable"

        output = result.stdout
        if isinstance(output, str) and any(message in output.casefold() for message in
                ("general failure", "unable to contact ip driver", "permission denied", "operation not permitted")):
            return "Ping Error"
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
