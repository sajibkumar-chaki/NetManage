# NETMANAGE — CI/CD Documentation

## 1. Project Overview

NETMANAGE is a Python-based Network Device Management System. The application supports device management, device searching, IP address validation, connectivity checks, network diagnostics, network reporting, and CSV export.

This document describes the project's automated testing process, GitHub Actions configuration, reporting and CSV export improvements, and continuous integration workflow.

## 2. CI/CD Overview

Continuous Integration (CI) is the process of automatically testing code changes when developers push updates or create pull requests.

Continuous Delivery/Deployment (CD) refers to preparing or automatically releasing software after successful validation.

NETMANAGE currently implements automated Continuous Integration through GitHub Actions. An automated deployment pipeline has not been configured.

## 3. GitHub Actions Configuration

**Workflow File:** `.github/workflows/tests.yml`

**Workflow Name:** NetManage Tests

**Execution Environment:** Ubuntu (GitHub-hosted runner)

**Python Version:** 3.12

**Testing Framework:** Pytest

The workflow is triggered by:

- Pushes to the `main` branch.
- Pushes to branches matching `feature/**`.
- Pull requests targeting the `main` branch.

## 4. CI Pipeline Execution

The GitHub Actions pipeline follows these steps:

1. **Checkout Repository:** GitHub Actions downloads the repository using `actions/checkout@v4`.
2. **Set Up Python:** Python 3.12 is configured using `actions/setup-python@v5`.
3. **Install Dependencies:** Required Python packages are installed using `pip install -r requirements.txt`.
4. **Run Automated Tests:** The command `python -m pytest -v` executes the automated test suite.
5. **Display Results:** GitHub Actions reports whether the workflow succeeded or failed.

## 5. Automated Testing

The project uses Pytest to verify application functionality.

Automated tests cover:

- Device management and searching.
- IP address validation.
- Connectivity and network diagnostics.
- Network reporting.
- CSV export.

### Reporting Improvements

The reporting function was updated to:

- Categorize unknown device types as Other.
- Handle empty device lists.
- Support case-insensitive device types.
- Remove leading and trailing spaces from device types.

Three new reporting tests were added.

### CSV Export Improvements

The CSV export function was updated to:

- Support empty device lists.
- Ignore additional device fields.
- Skip invalid records according to the defined validation rules.
- Preserve the existing CSV column structure.

Four additional automated tests verify CSV export behavior, including reading exported files and comparing their contents with expected data.

## 6. Local Testing Results

The existing project was tested before development changes were introduced.

**Baseline Result:** 30 tests passed.

Following the reporting improvements and addition of three reporting tests, 33 tests passed.

Following the CSV export improvements and addition of four CSV tests, the final local result was:

- Total automated tests: 37
- Passed: 37
- Failed: 0
- Execution time: 0.38 seconds
- Local Python version: 3.14.6
- Local Pytest version: 9.1.1

All 37 tests passed in the local development environment.

## 7. Environment and Dependency Management

The project uses `requirements.txt` to define its testing dependency.

The declared dependency is `pytest>=8.0,<9.0`.

The GitHub Actions workflow uses Python 3.12 and installs dependencies from this file.

The recorded local test run used Python 3.14.6 and Pytest 9.1.1. Therefore, successful local execution does not by itself verify the GitHub Actions environment.

## 8. GitHub Actions Verification Status

The existing workflow has been inspected and includes the commands required to discover and execute the new tests.

The updated feature branch has not yet been pushed to GitHub.

Therefore, GitHub Actions execution of the updated 37-test suite is **pending verification**.

After pushing the feature branch, the workflow execution and actual results must be checked in the GitHub Actions tab.

## 9. Development and Review Workflow

The development workflow follows these stages:

1. Clone the GitHub repository.
2. Create a dedicated feature branch.
3. Implement assigned development changes.
4. Add automated tests.
5. Run the complete test suite locally.
6. Commit the changes.
7. Push the feature branch to GitHub.
8. Verify GitHub Actions results.
9. Create a pull request targeting `main`.
10. Request code review and approval.
11. Merge the pull request after approval.

## 10. Evidence and Traceability

Development evidence includes:

- Feature branch creation.
- Reporting and CSV export code changes.
- New automated test implementations.
- Local test execution results.
- GitHub Actions workflow results after pushing.
- Pull request and code review.
- Merge confirmation after approval.

Screenshots and Git history must represent actual development activities. Existing contributions from other team members must not be attributed to this feature branch.

## 11. Conclusion

The reporting and CSV export functions have been improved, and seven new automated tests have been added.

The complete local test suite passed with 37 successful tests and zero failures.

The existing GitHub Actions configuration supports running the updated test suite. Final CI verification, pull request review, approval, and merge remain pending.