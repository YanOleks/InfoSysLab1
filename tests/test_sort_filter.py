import io

def _upload_test_files(client, auth_header):
    for name in ["a.py", "b.js", "c.png", "d.jpg"]:
        client.post("/files/upload",
            files={"file": (name, io.BytesIO(b"content"), "application/octet-stream")},
            headers=auth_header)

def test_sort_by_extension_asc(client, auth_header):
    _upload_test_files(client, auth_header)
    resp = client.get("/files?sort_by=extension&sort_order=asc", headers=auth_header)
    extensions = [f["extension"] for f in resp.json()]
    assert extensions == [".jpg", ".js", ".png", ".py"]

def test_sort_by_extension_desc(client, auth_header):
    _upload_test_files(client, auth_header)
    resp = client.get("/files?sort_by=extension&sort_order=desc", headers=auth_header)
    extensions = [f["extension"] for f in resp.json()]
    assert extensions == [".py", ".png", ".js", ".jpg"]

def test_filter_js_png(client, auth_header):
    _upload_test_files(client, auth_header)
    resp = client.get("/files?filter_ext=js_png", headers=auth_header)
    filenames = sorted([f["filename"] for f in resp.json()])
    assert filenames == ["b.js", "c.png"]
