"""Build a portable source archive without local device records or caches."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
target = root / "dist" / "NetManage-source.zip"
target.parent.mkdir(exist_ok=True)
excluded = {".git", ".pytest_cache", "__pycache__", ".venv", "dist", "data", "build", "history", "exports"}
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not excluded.intersection(relative.parts) and path.name != "test-results.xml":
            archive.write(path, Path("NetManage") / relative)
    archive.writestr("NetManage/data/devices.json", "[]\n")
print(target)

