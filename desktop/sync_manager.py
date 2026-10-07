import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

class SyncManager:
    def __init__(self, api_client, parent_window):
        self.api = api_client
        self.parent = parent_window
        self.local_folder = None

    def select_folder(self) -> str:
        self.local_folder = QFileDialog.getExistingDirectory(self.parent, "Select Folder to Sync")
        return self.local_folder

    def scan_folder(self) -> list:
        manifest = []
        if not self.local_folder:
            return manifest
            
        for f in os.listdir(self.local_folder):
            path = os.path.join(self.local_folder, f)
            if os.path.isfile(path):
                manifest.append({"filename": f, "size": os.path.getsize(path)})
        return manifest

    def sync(self) -> dict:
        manifest = self.scan_folder()
        delta = self.api.sync(manifest)

        uploaded = 0
        downloaded = 0
        
        for fname in delta.get("to_upload", []):
            path = os.path.join(self.local_folder, fname)
            if os.path.exists(path):
                try:
                    self.api.upload_file(path)
                    uploaded += 1
                except Exception:
                    pass
                    
        for item in delta.get("to_download", []):
            try:
                save_path = os.path.join(self.local_folder, item["filename"])
                self.api.download_file(item["id"], save_path)
                downloaded += 1
            except Exception:
                pass
                
        return {"uploaded": uploaded, "downloaded": downloaded}

    def run_sync(self):
        if not self.select_folder():
            return

        try:
            result = self.sync()
            QMessageBox.information(
                self.parent, 
                "Sync Complete", 
                f"Uploaded {result['uploaded']} files, downloaded {result['downloaded']} files"
            )
        except OSError as e:
            QMessageBox.warning(self.parent, "Error", f"Could not read folder: {e}")
        except Exception as e:
            QMessageBox.warning(self.parent, "Sync Error", f"Failed to sync with server: {e}")
