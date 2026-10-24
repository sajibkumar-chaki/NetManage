# NETMANAGE V2 technical handover

The original eight CLI features remain, with 9 still Exit. Options 10–12 provide Edit, Delete and bounded scheduled monitoring. The PySide6 desktop adds six pages using the same services; this is a desktop enhancement, not the web GUI backlog item.

## Start

```powershell
python app.py
python app.py --data-dir "C:/shared inventory"
python desktop.py
python desktop.py --data-dir "C:/shared inventory"
```

Install `requirements.txt` for tests; install `requirements-desktop.txt` for desktop use. See BUILD.md for packaging. Python 3.13 is the locally tested Windows environment; CI also retains Python 3.12 on Ubuntu.

## Data and validation

CLI default remains relative `data/devices.json`. Desktop uses `%LOCALAPPDATA%/NETMANAGE/devices.json` on Windows, independent of working/extraction directory. Both accept an explicit directory. Active storage is displayed. No silent migration occurs.

Back up the complete data directory before manual repair/import. About & data imports a valid legacy JSON list only into an empty store, preserving record IDs and source bytes. An existing empty destination receives a timestamped backup. Nonempty destinations and duplicate-address imports are rejected.

Malformed inventory/invalid records are rejected visibly and preserved, never replaced with an empty list. Saves use a same-directory temporary file, flush/fsync and atomic replacement. Nonblocking OS locks prevent concurrent transactions; each write reloads current inventory. The entire inventory is read-only during a monitor session. Persistent `.lock` files are normal: the OS releases locks on process exit. Use a local disk; network-filesystem semantics have not been tested.

Text fields must be nonblank, at most 255 characters and contain no control characters. Existing free-text device types remain supported. Addresses are canonicalized for Add/Edit comparison. Existing duplicates are warned about, never removed automatically. Deletion preserves all other record IDs. IP changes clear stored connectivity metadata; the dashboard also keys observations by device ID plus address.

## Monitoring

One device per session; defaults 5-second delay and 5 observations. Backend interval is finite >0 and <=3600 seconds; count is an integer 1–1000. Desktop minimum interval is 0.1 seconds. Delay begins after probe completion, so this is not exact real-time scheduling. Stop interrupts the delay; a running default probe has a subprocess timeout of 4 seconds. Close waits for bounded workers, without forced thread termination. No monitoring runs after exit.

History appends timezone-aware device snapshots and a session ID to `history/observations.jsonl`. Previous sessions remain. History is written before signalling success; failures surface. `Reachable`, `No Ping Response`, `Timeout` and `Ping Error` remain distinct. First observation is never recovery. Default ping uses validated literals, argument lists and a finite timeout. Windows zero exit additionally requires a reply measurement/TTL; localized output without recognizable evidence may conservatively show non-response. No latency, packet loss or uptime is invented.

Dashboard labels observations and marks those older than 60 seconds stale. Unchecked devices stay unchecked. Monitoring history displays the latest 500 rows. Diagnostics runs bounded network work off the GUI thread. GUI updates occur through signals. Multiple GUI processes can read, but conflicting writers receive a busy error.

CSV export retains existing invalid-record warning behavior with an optional GUI warning callback. Loaded inventory rejects invalid records before display; direct report callers still receive skipped-record counts. Export output lives separately under `exports/` when using default CLI export.

## Checks and evidence

All original tests are retained. Added backend and Qt integration tests use isolated stores and mocked probes. Windows CI installs Qt and runs them; CLI-only Ubuntu explicitly skips the new Qt module, while keeping original tests and backend tests. CI is unverified until the branch is authorized, pushed and its actual run inspected.

Run-specific progress, complete test logs, actual capture files and evidence register live outside the repository. The register distinguishes seeded inventory, mocked transitions, actual authorized loopback and historical-log displays. Offscreen Qt tests do not substitute for on-screen acceptance. Review findings are automated/self-review, not Sajib's independent approval.

## Demonstration

1. Dashboard: inventory/type totals, unchecked/stale labels and timestamps.
2. Devices: add a sample, edit it, cancel deletion, reject an equivalent duplicate address.
3. Monitor authorized loopback with a small bounded count; navigate while active, then Stop.
4. Show retained history and Reports CSV; restart and show persisted inventory.
5. About & data: active storage and runtime-only limitations.

## Remaining external gates

No release publication or merge is authorized by this document. Feature push/one PR requires the scoped user authorization; Sajib's genuine review and a separate head-specific merge authorization follow. A clean machine without Python has not been tested.
