import platform
import subprocess


def check_connectivity(ip_address, timeout=2):
    """Return Reachable or Unreachable using the operating system ping command."""
    system = platform.system().lower()
    command = ["ping", "-n" if system == "windows" else "-c", "1"]

    if system == "windows":
        command.append("-w")
        command.append(str(timeout * 1000))
    else:
        command.extend(["-W", str(timeout)])

    command.append(ip_address)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
            check=False,
        )
        return "Reachable" if result.returncode == 0 else "Unreachable"
    except (subprocess.SubprocessError, OSError):
        return "Unreachable"


def get_diagnostics(device):
    """Return basic diagnostic information for a device."""
    status = check_connectivity(device["ip_address"])

    return {
        "Hostname": device["hostname"],
        "IP Address": device["ip_address"],
        "Device Type": device["device_type"],
        "Location": device["location"],
        "Connectivity": status,
    }
