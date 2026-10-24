# NetManage

NetManage is a Python-based Network Device Management System developed as a four-member collaborative software project.

## Core Features

1. Add Network Device
2. View Devices
3. Search Device
4. Validate IPv4/IPv6 Address
5. Check Device Connectivity
6. Network Diagnostics
7. Generate Network Report
8. Export Device Data to CSV

## Technologies

- Python
- Git
- GitHub
- pytest
- GitHub Actions
- JSON
- CSV

## Project Structure

```text
NetManage/
├── app.py
├── device_manager.py
├── validation.py
├── network_tools.py
├── report.py
├── data/
├── tests/
├── .github/workflows/tests.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Run the Application

```bash
python app.py
```

## Install Test Dependency

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -q
```

## Team Collaboration

Each team member should work on a separate feature branch and use pull requests for review before merging into `main`.

Suggested branches:

- `feature/device-management`
- `feature/ip-validation`
- `feature/network-tools`
- `feature/testing-reporting`

## Activity 3 CI/CD

GitHub Actions automatically runs the pytest test suite on pushes and pull requests. A failed test prevents the change from being considered ready for integration.


## V2 desktop and inventory improvements

The CLI retains options 1�8 and 9 Exit, adding Edit (10), confirmed Delete (11) and bounded monitoring (12).
A PySide6 desktop shares the backend and adds Dashboard, Devices, Monitoring, Diagnostics, Reports and About/data pages.

```powershell
python -m pip install -r requirements.txt -r requirements-desktop.txt
python desktop.py
python app.py --data-dir "C:/shared inventory"
python desktop.py --data-dir "C:/shared inventory"
```

Desktop data defaults to `%LOCALAPPDATA%/NETMANAGE`; CLI keeps legacy `./data`. No automatic migration occurs.
See [V2 technical handover](V2_TECHNICAL_HANDOVER.md) for locking, safe import, validation, monitoring semantics, limitations and the demo sequence, and [BUILD.md](BUILD.md) for the native Windows one-folder distribution.
