import io

def test_upload_file(client, auth_header):
    file_content = b"print('hello')"
    response = client.post("/files/upload",
        files={"file": ("test.py", io.BytesIO(file_content), "application/octet-stream")},
        headers=auth_header)
    assert response.status_code == 200
    
    list_resp = client.get("/files", headers=auth_header)
    filenames = [f["filename"] for f in list_resp.json()]
    assert "test.py" in filenames

def test_download_file(client, auth_header):
    file_content = b"original content"
    client.post("/files/upload",
        files={"file": ("dl.txt", io.BytesIO(file_content), "application/octet-stream")},
        headers=auth_header)
        
    list_resp = client.get("/files", headers=auth_header)
    file_id = list_resp.json()[0]["id"]
    
    dl_resp = client.get(f"/files/{file_id}/download", headers=auth_header)
    assert dl_resp.status_code == 200
    assert dl_resp.content == file_content

def test_delete_file(client, auth_header):
    client.post("/files/upload",
        files={"file": ("del.txt", io.BytesIO(b"data"), "application/octet-stream")},
        headers=auth_header)
        
    list_resp = client.get("/files", headers=auth_header)
    file_id = list_resp.json()[0]["id"]
    
    del_resp = client.delete(f"/files/{file_id}", headers=auth_header)
    assert del_resp.status_code == 200
    
    list_resp2 = client.get("/files", headers=auth_header)
    assert len(list_resp2.json()) == 0
