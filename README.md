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
