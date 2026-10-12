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


The GitHub Actions workflow was successfully executed after pushing the feature branch.

### Verified CI Results

- Workflow: NetManage Tests
- Workflow Run: #24
- Branch: `feature/reporting-csv-ci`
- Commit: `4f4ffaf`
- Environment: Ubuntu
- Configured Python Version: 3.12
- Total Automated Tests: 37
- Tests Passed: 37
- Tests Failed: 0
- Test Execution Time: 0.35 seconds
- Workflow Status: Success

All 37 automated tests passed in GitHub Actions, including the seven newly added reporting and CSV export tests.

The results were verified using the GitHub Actions workflow logs.

These results apply to commit `4f4ffaf`. Any subsequent commits require a new CI verification.

Pull Request #5 has been created, and the Scrum Leader has requested changes. Final approval and merging remain pending.


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

Pull Request #5 is under review. The latest corrections passed 38 local automated tests and are awaiting updated GitHub Actions verification.

### Development Results

- Network Reporting: Improved
- CSV Export: Improved
- New Automated Tests: 7
- Total Automated Tests: 37
- Local Testing: 37 Passed, 0 Failed
- GitHub Actions CI: 37 Passed, 0 Failed
- GitHub Actions Workflow Run: #24
- Verified Commit: `4f4ffaf`
- CI Pipeline Status: Successful

The GitHub Actions workflow successfully executed all 37 automated tests using its configured Python 3.12 environment.

These CI results apply to commit `4f4ffaf`. Any subsequent documentation or code commits require a new workflow verification.

The project improvements have been implemented and successfully tested locally and through GitHub Actions.

Pull request submission, code review by the Scrum Leader, approval, and merging into the main branch remain pending.


## 12. Pull Request #5 – Review and Improvements

**Developer:** Shadid (Member 4 – QA/DevOps)
**Reviewer:** Sajib Kumar Chaki (Scrum Leader)
**Branch:** `feature/reporting-csv-ci`
**Status:** Changes requested; awaiting re-review

### Review Feedback and Improvements

The Scrum Leader requested two minor improvements:

1. **CSV Export:** Added a warning to inform users when invalid device records are skipped.
2. **Documentation:** Updated the pull request status and testing information.

An additional automated test was added to verify the CSV warning and ensure valid records are still exported correctly.

### Testing Results

| Test Information | Result |
|---|---|
| Previous automated tests | 37 passed |
| New warning test | 1 passed |
| **Updated local tests** | **38 passed, 0 failed** |
| Previous verified GitHub Actions | 37 passed |
| Updated GitHub Actions | Pending verification |

### Current Status

All 38 automated tests passed locally. The corrections are ready for GitHub submission.

After pushing the changes, GitHub Actions will run again. The Scrum Leader will then review the updated pull request before approval and merging.