"""NETMANAGE Qt Widgets desktop entry point; business logic lives in services."""
import argparse
import json
import os
import sys
import warnings
from collections import Counter
from datetime import datetime
from functools import wraps
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QMessageBox,
    QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QFileDialog, QAbstractItemView)
from device_manager import DeviceManager
from monitoring import MonitorSession
from network_tools import check_connectivity
from validation import validate_ip
from report import generate_report, export_csv

VERSION = "2.0.0"
STYLE = """
QWidget { background:#101824; color:#e5edf7; font-family:'Segoe UI'; font-size:14px; }
QMainWindow { background:#101824; }
QLabel#heading { font-size:27px; font-weight:700; }
QLabel#muted { color:#9eafc5; }
QLabel#card { background:#1b293b; border:1px solid #30435a; border-radius:10px; padding:20px; font-size:19px; }
QListWidget { background:#142031; border:0; padding:10px; min-width:165px; max-width:200px; }
QListWidget::item { padding:15px 10px; border-radius:6px; }
QListWidget::item:selected { background:#235276; color:#ffffff; }
QPushButton { background:#235276; border:1px solid #3b698a; border-radius:5px; padding:8px 14px; }
QPushButton:hover { background:#32688f; }
QPushButton:disabled { background:#273344; color:#7f8b9c; border-color:#354151; }
QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QPlainTextEdit { background:#192638; border:1px solid #41556d; border-radius:4px; padding:7px; }
QTableWidget { background:#142031; alternate-background-color:#1b293b; gridline-color:#30435a; border:1px solid #30435a; }
QHeaderView::section { background:#24364b; color:#c2d2e5; padding:10px; border:0; }
QTableWidget::item:selected { background:#235276; }
QDialog { background:#101824; }
"""


def guarded(fn):
    @wraps(fn)
    def wrapper(self, *args):
        try:
            return fn(self, *args)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            self.show_error(str(exc))
    return wrapper


def default_data_dir():
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "NETMANAGE"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "NETMANAGE"


def table(headers):
    widget = QTableWidget(0, len(headers))
    widget.setHorizontalHeaderLabels(headers)
    widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    widget.setAlternatingRowColors(True)
    widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    widget.horizontalHeader().setStretchLastSection(True)
    widget.verticalHeader().setVisible(False)
    return widget


def fill_table(widget, rows):
    widget.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            widget.setItem(r, c, QTableWidgetItem(str(value)))


class DeviceDialog(QDialog):
    def __init__(self, device=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit device" if device else "Add device")
        self.setMinimumWidth(440)
        layout = QFormLayout(self)
        self.fields = {}
        for key, label in [("hostname","Hostname"),("ip_address","IP address"),("device_type","Type"),("location","Location")]:
            field = QLineEdit(str((device or {}).get(key,"")))
            field.setMaxLength(255)
            field.setAccessibleName(label)
            layout.addRow(label,field)
            self.fields[key] = field
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self):
        return {k:v.text() for k,v in self.fields.items()}


class MonitorWorker(QThread):
    observed = Signal(dict)
    failed = Signal(str)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session

    def run(self):
        try:
            self.session.run(self.observed.emit)
        except Exception as exc:
            self.failed.emit(str(exc))

    def stop(self):
        self.session.stop()


class ProbeWorker(QThread):
    result = Signal(str, str)

    def __init__(self, address, parent=None):
        super().__init__(parent)
        self.address = address

    def run(self):
        try:
            self.result.emit(self.address, check_connectivity(self.address))
        except Exception as exc:
            self.result.emit(self.address, "Ping Error: " + str(exc))


class MainWindow(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.monitor = None
        self.probe_worker = None
        self.closing = False
        self.latest = {}
        self.setWindowTitle("NETMANAGE | Network operations")
        self.resize(1160, 760)
        self.setMinimumSize(900, 620)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0,0,0,0)
        self.nav = QListWidget()
        self.nav.addItems(["Dashboard", "Devices", "Monitoring", "Diagnostics", "Reports", "About & data"])
        self.nav.setAccessibleName("Navigation")
        outer.addWidget(self.nav)
        area = QVBoxLayout()
        area.setContentsMargins(24,22,24,18)
        outer.addLayout(area,1)
        top = QHBoxLayout()
        brand = QLabel("NETMANAGE")
        brand.setObjectName("heading")
        top.addWidget(brand)
        top.addStretch()
        subtitle = QLabel("NETWORK OPERATIONS  /  v" + VERSION)
        subtitle.setObjectName("muted")
        top.addWidget(subtitle)
        area.addLayout(top)
        self.stack = QStackedWidget()
        area.addWidget(self.stack,1)
        self.footer = QLabel("Inventory: " + str(manager.data_file))
        self.footer.setWordWrap(True)
        self.footer.setObjectName("muted")
        area.addWidget(self.footer)
        self.build_dashboard()
        self.build_devices()
        self.build_monitoring()
        self.build_diagnostics()
        self.build_reports()
        self.build_about()
        self.nav.currentRowChanged.connect(self.change_page)
        self.nav.setCurrentRow(0)
        self.refresh()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

    def page(self, title, description):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0,12,0,8)
        heading = QLabel(title)
        heading.setObjectName("heading")
        layout.addWidget(heading)
        info = QLabel(description)
        info.setWordWrap(True)
        info.setObjectName("muted")
        layout.addWidget(info)
        self.stack.addWidget(widget)
        return layout

    def build_dashboard(self):
        layout = self.page("Inventory overview", "Reachability describes the last recorded observation. It is not a live online/offline guarantee.")
        cards = QHBoxLayout()
        self.count_cards = []
        for title in ("Registered devices", "Reachable observations", "Not yet checked"):
            label = QLabel(title)
            label.setObjectName("card")
            label.setWordWrap(True)
            self.count_cards.append(label)
            cards.addWidget(label)
        layout.addLayout(cards)
        self.types = QLabel()
        layout.addWidget(self.types)
        self.dashboard_table = table(["Device", "Address", "Latest observation", "Last checked"])
        layout.addWidget(self.dashboard_table,1)
        button = QPushButton("Refresh inventory & history")
        button.clicked.connect(self.refresh)
        layout.addWidget(button)

    def build_devices(self):
        layout = self.page("Devices", "Manage the shared inventory. Editing and deletion are blocked while monitoring is active.")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search hostname, IP, type or location")
        self.search.setAccessibleName("Search devices")
        self.search.textChanged.connect(self.refresh_devices)
        layout.addWidget(self.search)
        self.device_table = table(["ID", "Hostname", "IP address", "Type", "Location"])
        layout.addWidget(self.device_table,1)
        buttons = QHBoxLayout()
        for label, handler in [("Add device",self.add_device),("Edit selected",self.edit_device),("Delete selected",self.delete_device),("Refresh",self.refresh)]:
            button = QPushButton(label)
            button.clicked.connect(handler)
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

    def build_monitoring(self):
        layout = self.page("Scheduled monitoring", "One registered device per session. Delay begins after each probe completes. Stop interrupts the delay; an active probe is bounded to about 4 seconds.")
        form = QFormLayout()
        self.device_combo = QComboBox()
        self.device_combo.setAccessibleName("Monitoring device")
        self.interval = QDoubleSpinBox()
        self.interval.setRange(.1,3600)
        self.interval.setValue(5)
        self.interval.setSuffix(" seconds")
        self.count = QSpinBox()
        self.count.setRange(1,1000)
        self.count.setValue(5)
        form.addRow("Device",self.device_combo)
        form.addRow("Delay after probe",self.interval)
        form.addRow("Observation count",self.count)
        layout.addLayout(form)
        buttons = QHBoxLayout()
        self.start_button = QPushButton("Start monitoring")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_monitor)
        self.stop_button.clicked.connect(self.stop_monitor)
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.stop_button)
        self.monitor_state = QLabel("Ready  ·  history is retained across sessions")
        buttons.addWidget(self.monitor_state,1)
        layout.addLayout(buttons)
        self.history_table = table(["Timestamp", "Device", "Address", "Result", "Event"])
        layout.addWidget(self.history_table,1)
        note = QLabel("Latest 500 saved observations shown. Monitoring runs only while NETMANAGE is open.")
        note.setObjectName("muted")
        layout.addWidget(note)

    def build_diagnostics(self):
        layout = self.page("Diagnostics", "Validate a literal IPv4/IPv6 address or run a real bounded ping. Only test devices you are authorised to contact.")
        self.diag_address = QLineEdit()
        self.diag_address.setPlaceholderText("Literal IPv4 or IPv6 address")
        self.diag_address.setAccessibleName("Diagnostic IP address")
        layout.addWidget(self.diag_address)
        row = QHBoxLayout()
        validate = QPushButton("Validate address")
        validate.clicked.connect(lambda:self.diag_output.setPlainText("Valid IP address" if validate_ip(self.diag_address.text()) else "Invalid IP address"))
        self.probe_button = QPushButton("Check connectivity")
        self.probe_button.clicked.connect(self.start_probe)
        row.addWidget(validate)
        row.addWidget(self.probe_button)
        row.addStretch()
        layout.addLayout(row)
        self.diag_output = QPlainTextEdit()
        self.diag_output.setReadOnly(True)
        layout.addWidget(self.diag_output,1)

    def build_reports(self):
        layout = self.page("Reports", "Inventory summary and CSV export. Cancelled save dialogs leave files unchanged.")
        self.report_text = QPlainTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text,1)
        export = QPushButton("Save inventory CSV…")
        export.clicked.connect(self.export_report)
        layout.addWidget(export)

    def build_about(self):
        layout = self.page("About & data", "NETMANAGE " + VERSION + "  ·  PySide6 desktop and shared Python backend")
        description = QLabel("Inventory: " + str(self.manager.data_file) + "\n\nHistory: " + str(self.history_path) +
            "\n\nNo service runs after exit. No background monitoring, discovery, SNMP or automatic migration."
            "\n\nImport accepts a valid legacy JSON list only into an empty store. Existing empty files are backed up."
            "\n\nCLI: python app.py --data-dir <this directory>\nDesktop: python desktop.py [--data-dir <directory>]"
            "\n\nOriginal team contributions are retained in Git history.")
        description.setWordWrap(True)
        description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(description)
        import_button = QPushButton("Import legacy inventory…")
        import_button.clicked.connect(self.import_inventory)
        layout.addWidget(import_button)
        layout.addStretch()

    @property
    def history_path(self):
        return self.manager.data_file.parent / "history" / "observations.jsonl"

    def show_error(self, message):
        self.statusBar().showMessage(message)
        QMessageBox.warning(self,"NETMANAGE",message)

    @guarded
    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        self.refresh()

    def read_history(self):
        if not self.history_path.exists():
            return []
        rows = []
        with self.history_path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                    if not isinstance(row,dict) or not all(k in row for k in ("timestamp","device_id","hostname","address","result","event")):
                        raise ValueError("Missing history fields")
                    rows.append(row)
                except ValueError:
                    self.statusBar().showMessage("Warning: malformed history record omitted; source file preserved.")
        return rows

    @guarded
    def refresh(self, *args):
        devices = self.manager.get_all_devices()
        history = self.read_history()
        self.latest = {(r["device_id"],r["address"]):r for r in history}
        checked = [self.latest.get((d["id"],d["ip_address"])) for d in devices]
        reachable = sum(bool(r and r["result"] == "Reachable") for r in checked)
        for label,title,value in zip(self.count_cards,("Registered devices","Reachable observations","Not yet checked"),(len(devices),reachable,sum(r is None for r in checked))):
            label.setText(f"{value}\n{title}")
        self.types.setText("   ·   ".join(f"{key}: {value}" for key,value in sorted(Counter(d["device_type"] for d in devices).items())) or "No devices registered")
        rows=[]
        for device,obs in zip(devices,checked):
            status="Unchecked"
            if obs:
                try:
                    age=(datetime.now().astimezone()-datetime.fromisoformat(obs["timestamp"])).total_seconds()
                    status=obs["result"] + (" (stale)" if age>60 else " (last observed)")
                except (ValueError,TypeError):
                    status=obs["result"] + " (timestamp unverified)"
            rows.append([device["hostname"],device["ip_address"],status,obs["timestamp"] if obs else "—"])
        fill_table(self.dashboard_table,rows)
        fill_table(self.history_table,[[r[k] for k in ("timestamp","hostname","address","result","event")] for r in history[-500:]])
        previous = self.device_combo.currentData()
        self.device_combo.clear()
        for d in devices:
            self.device_combo.addItem(f"{d['id']} · {d['hostname']} · {d['ip_address']}",d["id"])
        selected=self.device_combo.findData(previous)
        if selected>=0:self.device_combo.setCurrentIndex(selected)
        self.report_text.setPlainText(generate_report(devices))
        self.refresh_devices()

    @guarded
    def refresh_devices(self, *args):
        term=self.search.text().strip()
        devices=self.manager.search_devices(term) if term else self.manager.get_all_devices()
        fill_table(self.device_table,[[d[k] for k in ("id","hostname","ip_address","device_type","location")] for d in devices])

    def selected_device(self):
        row=self.device_table.currentRow()
        if row<0:raise ValueError("Select a device first.")
        device=self.manager.get_device(int(self.device_table.item(row,0).text()))
        if device is None:raise ValueError("Device no longer exists. Refresh inventory.")
        return device

    @guarded
    def add_device(self):
        dialog=DeviceDialog(parent=self)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            self.manager.add_device(**dialog.values())
            self.refresh()
            self.statusBar().showMessage("Device added.")

    @guarded
    def edit_device(self):
        device=self.selected_device()
        dialog=DeviceDialog(device,self)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            self.manager.edit_device(device["id"],expected_device=device,**dialog.values())
            self.refresh()
            self.statusBar().showMessage("Device updated.")

    @guarded
    def delete_device(self):
        device=self.selected_device()
        answer=QMessageBox.question(self,"Confirm deletion",f"Delete #{device['id']} {device['hostname']} ({device['ip_address']})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if answer==QMessageBox.StandardButton.Yes:
            self.manager.delete_device(device["id"],True,expected_device=device)
            self.refresh()
            self.statusBar().showMessage("Device deleted.")

    @guarded
    def start_monitor(self):
        if self.monitor is not None:raise ValueError("Monitoring is already active.")
        ident=self.device_combo.currentData()
        if ident is None:raise ValueError("Register a device first.")
        session=MonitorSession(self.manager,ident,interval=self.interval.value(),count=self.count.value())
        self.monitor=MonitorWorker(session,self)
        self.monitor.observed.connect(self.observation)
        self.monitor.failed.connect(self.show_error)
        self.monitor.finished.connect(self.monitor_finished)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.monitor_state.setText("Running · observations saved before display")
        self.monitor.start()

    def observation(self,row):
        self.monitor_state.setText(row["result"] + " · history saved")
        self.refresh()

    def stop_monitor(self):
        if self.monitor:
            self.monitor.stop()
            self.monitor_state.setText("Stopping after bounded probe…")

    def monitor_finished(self):
        worker=self.monitor
        self.monitor=None
        worker.deleteLater()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.monitor_state.setText("Stopped / complete · saved history retained")
        if self.closing:QTimer.singleShot(0,self.close)

    @guarded
    def start_probe(self):
        if self.probe_worker is not None:return
        address=self.diag_address.text().strip()
        if not validate_ip(address):raise ValueError("Enter a valid literal IP address.")
        self.probe_worker=ProbeWorker(address,self)
        self.probe_worker.result.connect(lambda ip,status:self.diag_output.setPlainText(datetime.now().astimezone().isoformat()+"\n"+ip+"\n"+status))
        self.probe_worker.finished.connect(self.probe_finished)
        self.probe_button.setEnabled(False)
        self.probe_worker.start()

    def probe_finished(self):
        worker=self.probe_worker
        self.probe_worker=None
        worker.deleteLater()
        self.probe_button.setEnabled(True)
        if self.closing:QTimer.singleShot(0,self.close)

    @guarded
    def export_report(self):
        filename,_=QFileDialog.getSaveFileName(self,"Save inventory CSV",str(self.manager.data_file.parent / "exports" / "devices.csv"),"CSV files (*.csv)")
        if not filename:return
        messages=[]
        export_csv(self.manager.get_all_devices(),filename,on_warning=messages.append)
        self.statusBar().showMessage("Exported: " + filename)
        if messages:QMessageBox.warning(self,"Export warning","\n".join(messages))

    @guarded
    def import_inventory(self):
        filename,_=QFileDialog.getOpenFileName(self,"Import legacy inventory","","JSON files (*.json)")
        if not filename:return
        count=self.manager.import_inventory(filename)
        self.refresh()
        self.statusBar().showMessage(f"Imported {count} records. Original source preserved.")

    def closeEvent(self,event):
        if self.monitor is not None or self.probe_worker is not None:
            self.closing=True
            self.timer.stop()
            self.stop_monitor()
            self.statusBar().showMessage("Closing safely after bounded worker completion…")
            event.ignore()
        else:
            event.accept()


def main():
    parser=argparse.ArgumentParser(description="NETMANAGE desktop")
    parser.add_argument("--data-dir",type=Path,default=default_data_dir())
    args=parser.parse_args()
    app=QApplication(sys.argv[:1])
    app.setApplicationName("NETMANAGE")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    try:
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            manager=DeviceManager(args.data_dir / "devices.json")
        window=MainWindow(manager)
        window.show()
        if recorded:
            QTimer.singleShot(0,lambda:window.show_error("\n".join(str(w.message) for w in recorded)))
    except (ValueError,OSError) as exc:
        QMessageBox.critical(None,"Cannot open inventory",str(exc))
        return 1
    return app.exec()


if __name__=="__main__":
    raise SystemExit(main())
