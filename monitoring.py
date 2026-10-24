"""Bounded foreground monitoring with immutable JSONL observations."""
import json
import math
import threading
import uuid
from datetime import datetime
from pathlib import Path
from device_manager import file_lock
from network_tools import check_connectivity


def validate_schedule(interval, count):
    if isinstance(interval, bool) or not isinstance(interval, (int, float)) or not math.isfinite(interval) or not 0 < interval <= 3600:
        raise ValueError("Interval must be finite, greater than 0 and at most 3600 seconds.")
    if type(count) is not int or not 1 <= count <= 1000:
        raise ValueError("Count must be an integer from 1 to 1000.")


def transition(previous, current):
    if previous in ("No Ping Response", "Timeout") and current == "Reachable":
        return "Recovery observed"
    if previous == "Reachable" and current in ("No Ping Response", "Timeout"):
        return "Non-response observed"
    return "Observation" if current in ("Reachable", "No Ping Response", "Timeout") else "Operational error"


class MonitorSession:
    def __init__(self, manager, device_id, history_file=None, interval=5, count=5, probe=None):
        validate_schedule(interval, count)
        self.manager, self.device_id = manager, device_id
        self.interval, self.count = interval, count
        self.history_file = Path(history_file or manager.data_file.parent / "history" / "observations.jsonl")
        self.probe = probe or check_connectivity
        self.cancelled = threading.Event()
        self.session_id = uuid.uuid4().hex

    def stop(self):
        self.cancelled.set()

    def run(self, on_result=lambda observation: None):
        # Entire store is read-only during monitoring, including other processes.
        with file_lock(self.manager.monitor_lock):
            device = self.manager.get_device(self.device_id)
            if device is None:
                raise ValueError("Device not found.")
            previous = None
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            for index in range(self.count):
                if self.cancelled.is_set():
                    break
                result = self.probe(device["ip_address"])
                row = dict(session_id=self.session_id, timestamp=datetime.now().astimezone().isoformat(),
                           device_id=device["id"], hostname=device["hostname"], address=device["ip_address"],
                           result=result, event=transition(previous, result))
                # Surface write failures; never announce successful persistence first.
                with file_lock(self.history_file.with_suffix(".lock")):
                    with self.history_file.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(row) + "\n")
                        handle.flush()
                on_result(row)
                previous = result
                if index + 1 < self.count and self.cancelled.wait(self.interval):
                    break
