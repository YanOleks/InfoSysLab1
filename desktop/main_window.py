import os
from PySide6.QtWidgets import (
    QMainWindow, QTableView, QToolBar, QMessageBox, QFileDialog, 
    QComboBox, QStatusBar
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtCore import Qt, QSortFilterProxyModel

from preview_dialog import PreviewDialog
from sync_manager import SyncManager

class MainWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setWindowTitle("Lightweight Drive")
        self.resize(800, 600)
        self.setAcceptDrops(True)
        
        self._setup_toolbar()
        self._setup_table()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.refresh_files()

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        upload_act = QAction("Upload", self)
        upload_act.triggered.connect(self.upload_file)
        toolbar.addAction(upload_act)
        
        download_act = QAction("Download", self)
        download_act.triggered.connect(self.download_file)
        toolbar.addAction(download_act)
        
        delete_act = QAction("Delete", self)
        delete_act.triggered.connect(self.delete_file)
        toolbar.addAction(delete_act)
        
        sync_act = QAction("Sync", self)
        sync_act.triggered.connect(self.sync_files)
        toolbar.addAction(sync_act)
        
        refresh_act = QAction("Refresh", self)
        refresh_act.triggered.connect(self.refresh_files)
        toolbar.addAction(refresh_act)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Всі файли", "Тільки .js та .png"])
        self.filter_combo.currentIndexChanged.connect(self.refresh_files)
        toolbar.addWidget(self.filter_combo)

        view_menu = self.menuBar().addMenu("View")
        self.col_actions = []
        col_names = ["Назва", "Тип", "Дата створення", "Дата зміни", "Завантажив", "Останній редактор"]
        for i, name in enumerate(col_names):
            act = QAction(name, self, checkable=True)
            act.setChecked(True)
            if i == 0:
                act.setEnabled(False) # Назва завжди видима
            act.toggled.connect(lambda checked, col=i: self.table_view.setColumnHidden(col, not checked))
            view_menu.addAction(act)
            self.col_actions.append(act)

    def _setup_table(self):
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setSortingEnabled(True)
        self.table_view.doubleClicked.connect(self.on_double_click)
        
        self.model = QStandardItemModel(0, 6)
        self.model.setHorizontalHeaderLabels([
            "Назва", "Тип", "Дата створення", "Дата зміни", "Завантажив", "Останній редактор"
        ])
        
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        
        self.setCentralWidget(self.table_view)

    def refresh_files(self):
        filter_ext = None
        if self.filter_combo.currentIndex() == 1:
            filter_ext = "js_png"
            
        try:
            files = self.api_client.list_files(filter_ext=filter_ext)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to list files: {e}")
            return
            
        self.model.removeRows(0, self.model.rowCount())
        for f in files:
            row = [
                QStandardItem(f["filename"]),
                QStandardItem(f["extension"]),
                QStandardItem(f["created_at"]),
                QStandardItem(f["updated_at"]),
                QStandardItem(f["uploaded_by_username"]),
                QStandardItem(f["last_modified_by_username"])
            ]
            row[0].setData(f["id"], Qt.UserRole)
            for item in row:
                item.setEditable(False)
            self.model.appendRow(row)

    def get_selected_file_id(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None
        proxy_index = indexes[0]
        model_index = self.proxy_model.mapToSource(proxy_index)
        item = self.model.item(model_index.row(), 0)
        return item.data(Qt.UserRole)

    def get_selected_filename(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None
        proxy_index = indexes[0]
        model_index = self.proxy_model.mapToSource(proxy_index)
        return self.model.item(model_index.row(), 0).text()

    def upload_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if filepath:
            try:
                self.api_client.upload_file(filepath)
                self.status_bar.showMessage("Uploaded 1 file", 3000)
                self.refresh_files()
            except Exception as e:
                QMessageBox.warning(self, "Upload Error", str(e))

    def download_file(self):
        file_id = self.get_selected_file_id()
        if not file_id:
            return
        filename = self.get_selected_filename()
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File As", filename)
        if save_path:
            try:
                self.api_client.download_file(file_id, save_path)
                self.status_bar.showMessage(f"Downloaded {filename}", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Download Error", str(e))

    def delete_file(self):
        file_id = self.get_selected_file_id()
        if not file_id:
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this file?")
        if reply == QMessageBox.Yes:
            try:
                self.api_client.delete_file(file_id)
                self.refresh_files()
            except Exception as e:
                QMessageBox.warning(self, "Delete Error", str(e))

    def on_double_click(self, index):
        model_index = self.proxy_model.mapToSource(index)
        file_id = self.model.item(model_index.row(), 0).data(Qt.UserRole)
        filename = self.model.item(model_index.row(), 0).text()
        ext = self.model.item(model_index.row(), 1).text().lower()
        
        if ext in [".py", ".jpg"]:
            try:
                file_type, content = self.api_client.preview_file(file_id)
                dlg = PreviewDialog(filename, file_type, content, self)
                dlg.exec()
            except Exception as e:
                QMessageBox.warning(self, "Preview Error", str(e))

    def sync_files(self):
        sync_mgr = SyncManager(self.api_client, self)
        sync_mgr.run_sync()
        self.refresh_files()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        uploaded = 0
        for url in urls:
            if url.isLocalFile():
                filepath = url.toLocalFile()
                try:
                    self.api_client.upload_file(filepath)
                    uploaded += 1
                except Exception:
                    pass
        if uploaded > 0:
            self.status_bar.showMessage(f"Uploaded {uploaded} files", 3000)
            self.refresh_files()
