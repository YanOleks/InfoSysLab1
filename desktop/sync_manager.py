import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

class SyncManager:
    def __init__(self, api_client, parent_window):
        self.api = api_client
        self.parent = parent_window

    def run_sync(self):
        folder = QFileDialog.getExistingDirectory(self.parent, "Select Folder to Sync")
        if not folder:
            return

        manifest = []
        try:
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    manifest.append({"filename": f, "size": os.path.getsize(path)})
        except Exception as e:
            QMessageBox.warning(self.parent, "Error", f"Could not read folder: {e}")
            return
        
        try:
            delta = self.api.sync(manifest)
        except Exception as e:
            QMessageBox.warning(self.parent, "Sync Error", f"Failed to sync with server: {e}")
            return

        uploaded = 0
        downloaded = 0
        
        for fname in delta.get("to_upload", []):
            path = os.path.join(folder, fname)
            if os.path.exists(path):
                try:
                    self.api.upload_file(path)
                    uploaded += 1
                except Exception:
                    pass
                    
        for item in delta.get("to_download", []):
            try:
                save_path = os.path.join(folder, item["filename"])
                self.api.download_file(item["id"], save_path)
                downloaded += 1
            except Exception:
                pass
                
        QMessageBox.information(
            self.parent, 
            "Sync Complete", 
            f"Uploaded {uploaded} files, downloaded {downloaded} files"
        )
