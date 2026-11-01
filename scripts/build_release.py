"""Build source from an explicit manifest; never scan local runtime data."""
from pathlib import Path
import zipfile

# Add new source files here deliberately. Untracked files, custom data folders,
# credentials, virtual environments and caches must never enter the archive.
RELEASE_FILES = (
    ".gitignore",
    ".github/workflows/tests.yml",
    "app.py",
    "BUILD.md",
    "CI_CD_DOCUMENTATION.md",
    "desktop.py",
    "device_manager.py",
    "monitoring.py",
    "NETMANAGE.spec",
    "network_tools.py",
    "README.md",
    "report.py",
    "requirements-build.txt",
    "requirements-desktop.txt",
    "requirements.txt",
    "scripts/build_release.py",
    "TEAM_PLAN.md",
    "TEST_CASES.md",
    "test_search_manual.py",
    "tests/test_device_manager_2.py",
    "tests/test_device_manager.py",
    "tests/test_network_tools.py",
    "tests/test_report.py",
    "tests/test_v2_backend.py",
    "tests/test_v2_desktop.py",
    "tests/test_validation_2.py",
    "tests/test_validation.py",
    "V2_TECHNICAL_HANDOVER.md",
    "validation.py",
)

root = Path(__file__).resolve().parents[1]
target = root / "dist" / "NetManage-source.zip"
# Validate the whole manifest before opening the output archive. Reject links
# so a listed path cannot point at a local file outside the intended source.
for name in RELEASE_FILES:
    path = root / name
    if not path.is_file():
        raise FileNotFoundError(f"Required release file is missing: {name}")
    if any(part.is_symlink() for part in (path, *path.parents) if part != root and root in part.parents):
        raise ValueError(f"Release file must not use a symbolic link: {name}")

target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(RELEASE_FILES):
        archive.write(root / name, "NetManage/" + name)
    archive.writestr("NetManage/data/devices.json", "[]\n")
print(target)

