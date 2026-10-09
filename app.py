from device_manager import DeviceManager
from validation import validate_ip
from network_tools import check_connectivity, get_diagnostics
from report import generate_report, export_csv


def display_menu():
    print("\n" + "=" * 50)
    print("              NETMANAGE")
    print("       Network Device Management System")
    print("=" * 50)
    print("1. Add Network Device")
    print("2. View Devices")
    print("3. Search Device")
    print("4. Validate IP Address")
    print("5. Check Connectivity")
    print("6. Network Diagnostics")
    print("7. Generate Network Report")
    print("8. Export Device Data")
    print("9. Exit")


def add_device(manager):
    print("\n--- Add Network Device ---")

    hostname = input("Hostname: ").strip()
    ip_address = input("IP address: ").strip()
    device_type = input(
        "Device type (Router/Switch/Server/Other): "
    ).strip()
    location = input("Location: ").strip()

    if not hostname or not ip_address or not device_type or not location:
        print("Error: all fields are required.")
        return

    if not validate_ip(ip_address):
        print("Error: invalid IP address.")
        return

    try:
        device = manager.add_device(
            hostname,
            ip_address,
            device_type,
            location
        )
        print(f"Device added successfully with ID {device['id']}.")

    except ValueError as error:
        print(f"Error: {error}")


def view_devices(manager):
    print("\n--- All Devices ---")

    devices = manager.get_all_devices()

    if not devices:
        print("No devices found.")
        return

    print(
        f"{'ID':<5}"
        f"{'Hostname':<18}"
        f"{'IP Address':<18}"
        f"{'Type':<12}"
        f"{'Location':<15}"
    )

    print("-" * 68)

    for device in devices:
        print(
            f"{device['id']:<5}"
            f"{device['hostname']:<18}"
            f"{device['ip_address']:<18}"
            f"{device['device_type']:<12}"
            f"{device['location']:<15}"
        )


def search_device(manager):
    term = input(
        "\nEnter hostname, IP address, or device type: "
    ).strip()

    results = manager.search_devices(term)

    if not results:
        print("No matching devices found.")
        return

    print(f"\nFound {len(results)} device(s):")

    for device in results:
        print(
            f"ID: {device['id']} | "
            f"{device['hostname']} | "
            f"{device['ip_address']} | "
            f"{device['device_type']} | "
            f"{device['location']}"
        )


def validate_ip_menu():
    ip_address = input("\nEnter IP address: ").strip()

    if validate_ip(ip_address):
        print("Valid IP address.")
    else:
        print("Invalid IP address.")


def connectivity_menu(manager):
    devices = manager.get_all_devices()

    if not devices:
        print("No devices available.")
        return

    view_devices(manager)

    try:
        device_id = int(input("\nEnter device ID: "))
    except ValueError:
        print("Invalid device ID.")
        return

    device = manager.get_device(device_id)

    if not device:
        print("Device not found.")
        return

    print(f"Checking connectivity to {device['ip_address']}...")

    result = check_connectivity(device["ip_address"])

    print(f"Status: {result}")


def diagnostics_menu(manager):
    try:
        device_id = int(input("\nEnter device ID: "))
    except ValueError:
        print("Invalid device ID.")
        return

    device = manager.get_device(device_id)

    if not device:
        print("Device not found.")
        return

    diagnostics = get_diagnostics(device)

    print("\n--- Network Diagnostics ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")


def main():
    manager = DeviceManager()

    while True:
        display_menu()

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            add_device(manager)

        elif choice == "2":
            view_devices(manager)

        elif choice == "3":
            search_device(manager)

        elif choice == "4":
            validate_ip_menu()

        elif choice == "5":
            connectivity_menu(manager)

        elif choice == "6":
            diagnostics_menu(manager)

        elif choice == "7":
            report = generate_report(manager.get_all_devices())
            print("\n" + report)

        elif choice == "8":
            filename = export_csv(manager.get_all_devices())
            print(f"Device data exported to {filename}")

        elif choice == "9":
            print("Thank you for using NetManage.")
            break

        else:
            print("Invalid choice. Please select 1-9.")


if __name__ == "__main__":
    main()