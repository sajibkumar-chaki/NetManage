# Native Windows build

Use Python 3.13 on Windows and an isolated environment. Keep the complete one-folder output together.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python -m pytest -v
.\.venv\Scripts\python -m PyInstaller NETMANAGE.spec --distpath dist --workpath build
```

Launch `dist/NETMANAGE/NETMANAGE.exe`. ZIP the whole `NETMANAGE` folder, including `_internal`.
Do not bundle inventories, monitoring history or a virtual environment. Build on native Windows.
Dependencies are pinned at the Qt/PyInstaller entry points; the delivery includes the exact tested environment freeze and copied dependency notices.

Default desktop data is `%LOCALAPPDATA%/NETMANAGE`. Override with `--data-dir "C:/path with spaces/data"`.
The CLI retains `./data` by default; use `python app.py --data-dir "C:/same/path"` to share the store.
The executable is unsigned. Developer-machine launch tests are not clean-machine certification.

Upstream documentation: https://doc.qt.io/qtforpython-6/gettingstarted.html and https://pyinstaller.org/en/stable/usage.html.

The spec excludes tool-PATH ICU copies: Qt uses the supported Windows OS ICU shim. The first experimental package exposed this collision and is retained only as failed-run evidence.
