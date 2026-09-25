import httpx
import os
from typing import Optional, Union, Tuple, List

class ApiClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.client = httpx.Client(base_url=base_url, timeout=30.0)

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def register(self, username: str, password: str) -> dict:
        response = self.client.post(
            "/auth/register",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def login(self, username: str, password: str) -> str:
        response = self.client.post(
            "/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return self.token

    def list_files(
        self,
        sort_by: str = "filename",
        sort_order: str = "asc",
        filter_ext: Optional[str] = None
    ) -> List[dict]:
        params = {"sort_by": sort_by, "sort_order": sort_order}
        if filter_ext:
            params["filter_ext"] = filter_ext
            
        response = self.client.get(
            "/files",
            params=params,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def upload_file(self, filepath: str) -> dict:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            response = self.client.post(
                "/files/upload",
                files={"file": (filename, f, "application/octet-stream")},
                headers=self._headers()
            )
        response.raise_for_status()
        return response.json()

    def download_file(self, file_id: int, save_path: str) -> None:
        with self.client.stream("GET", f"/files/{file_id}/download", headers=self._headers()) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

    def delete_file(self, file_id: int) -> None:
        response = self.client.delete(f"/files/{file_id}", headers=self._headers())
        response.raise_for_status()

    def preview_file(self, file_id: int) -> Tuple[str, Union[str, bytes]]:
        response = self.client.get(f"/files/{file_id}/preview", headers=self._headers())
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
            return data["type"], data["content"]
        else:
            return "image", response.content

    def sync(self, manifest: List[dict]) -> dict:
        response = self.client.post(
            "/files/sync",
            json={"files": manifest},
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
