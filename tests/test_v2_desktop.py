import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import threading
import time
from unittest.mock import patch
import pytest
pytest.importorskip("PySide6", reason="CLI-only environment; Windows desktop job runs Qt tests")
from PySide6.QtCore import QCoreApplication,QEvent
from PySide6.QtWidgets import QApplication,QDialog,QMessageBox
from device_manager import DeviceManager
from desktop import MainWindow,DeviceDialog,MonitorWorker
from monitoring import MonitorSession


@pytest.fixture(scope="module")
def qtapp():
    app=QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    yield app
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    app.processEvents()


@pytest.fixture
def window(qtapp,tmp_path):
    m=DeviceManager(tmp_path / "devices.json")
    m.add_device("Demo","127.0.0.1","Server","Lab")
    w=MainWindow(m)
    yield w
    if w.monitor:w.monitor.stop();w.monitor.wait(2000)
    w.timer.stop()
    w.close()
    w.deleteLater()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    qtapp.processEvents()


def pump(app,condition,seconds=3):
    deadline=time.monotonic()+seconds
    while not condition() and time.monotonic()<deadline:
        app.processEvents()
        time.sleep(.005)
    assert condition()


def test_ui_edit_delete_cancel_and_persistence(window,monkeypatch):
    window.nav.setCurrentRow(1)
    window.device_table.selectRow(0)
    before=window.manager.data_file.read_bytes()
    monkeypatch.setattr(DeviceDialog,"exec",lambda self:QDialog.DialogCode.Rejected)
    window.edit_device()
    monkeypatch.setattr(QMessageBox,"question",lambda *args:QMessageBox.StandardButton.No)
    window.delete_device()
    assert window.manager.data_file.read_bytes()==before
    monkeypatch.setattr(DeviceDialog,"exec",lambda self:QDialog.DialogCode.Accepted)
    monkeypatch.setattr(DeviceDialog,"values",lambda self:dict(hostname="Changed",ip_address="127.0.0.1",device_type="Server",location="Lab"))
    window.edit_device()
    assert DeviceManager(window.manager.data_file).get_device(1)["hostname"]=="Changed"
    window.device_table.selectRow(0)
    monkeypatch.setattr(QMessageBox,"question",lambda *args:QMessageBox.StandardButton.Yes)
    window.delete_device()
    assert DeviceManager(window.manager.data_file).get_all_devices()==[]


def test_monitor_worker_stop_and_clean_close(window,qtapp):
    gate=threading.Event()
    entered=threading.Event()
    def probe(ip):
        entered.set()
        gate.wait(1)
        return "Reachable"
    with patch("monitoring.check_connectivity",probe):
        window.interval.setValue(3600)
        window.start_monitor()
        assert window.monitor is not None
        assert entered.wait(1)
        window.close()
        assert window.closing
        assert window.monitor is not None
        gate.set()
        pump(qtapp,lambda:window.monitor is None)
        assert len(window.read_history())==1
        assert window.start_button.isEnabled()
        assert not window.stop_button.isEnabled()


def test_monitor_observation_on_gui_thread(window,qtapp):
    threads=[]
    session=MonitorSession(window.manager,1,count=1,probe=lambda ip:"Reachable")
    worker=MonitorWorker(session)
    worker.observed.connect(lambda row:threads.append(threading.get_ident()))
    worker.start()
    pump(qtapp,lambda:bool(threads))
    worker.wait(1000)
    assert threads==[threading.get_ident()]
    worker.deleteLater()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)


def test_csv_cancel_and_error(window,monkeypatch,tmp_path):
    from PySide6.QtWidgets import QFileDialog
    monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *args:("",""))
    window.export_report()
    errors=[]
    window.show_error=errors.append
    monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *args:(str(tmp_path),""))
    window.export_report()
    assert errors


def test_import_preserves_ids_and_rejects_nonempty(tmp_path):
    source=DeviceManager(tmp_path/"source.json")
    source.add_device("A","::1","Server","Lab")
    source.add_device("B","127.0.0.1","Server","Lab")
    source.delete_device(1,True)
    dest=DeviceManager(tmp_path/"dest.json")
    assert dest.import_inventory(source.data_file)==1
    assert dest.get_device(2)["hostname"]=="B"
    with pytest.raises(ValueError,match="empty"):dest.import_inventory(source.data_file)


def test_ip_change_does_not_reuse_history(window):
    MonitorSession(window.manager,1,count=1,probe=lambda ip:"Reachable").run()
    window.refresh()
    assert "Reachable" in window.dashboard_table.item(0,2).text()
    window.manager.edit_device(1,ip_address="::1")
    window.refresh()
    assert window.dashboard_table.item(0,2).text()=="Unchecked"
