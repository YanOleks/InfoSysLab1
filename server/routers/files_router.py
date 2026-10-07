import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, aliased
from database import get_db
from models import User, File
from auth import get_current_user
from schemas import FileMetadata, SyncManifest, SyncDelta

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.get("", response_model=list[FileMetadata])
def list_files(
    sort_by: str = Query("filename"),
    sort_order: str = Query("asc"),
    filter_ext: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    Uploader = aliased(User)
    Modifier = aliased(User)
    
    query = db.query(
        File, 
        Uploader.username.label("uploaded_by_username"), 
        Modifier.username.label("last_modified_by_username")
    )\
    .join(Uploader, File.uploaded_by == Uploader.id)\
    .join(Modifier, File.last_modified_by == Modifier.id)\
    .filter(File.owner_id == current_user.id)
        
    if filter_ext:
        allowed_exts = [f".{ext}" for ext in filter_ext.split("_")]
        query = query.filter(File.extension.in_(allowed_exts))
        
    if hasattr(File, sort_by):
        sort_col = getattr(File, sort_by)
        if sort_order == "desc":
            sort_col = sort_col.desc()
        query = query.order_by(sort_col)
    
    results = query.all()
    
    response = []
    for file_obj, up_name, mod_name in results:
        response.append({
            "id": file_obj.id,
            "filename": file_obj.filename,
            "extension": file_obj.extension,
            "file_size": file_obj.file_size,
            "created_at": file_obj.created_at,
            "updated_at": file_obj.updated_at,
            "uploaded_by_username": up_name,
            "last_modified_by_username": mod_name
        })
        
    return response

@router.post("/upload")
def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
        
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()
    
    user_dir = f"storage/{current_user.id}"
    os.makedirs(user_dir, exist_ok=True)
    storage_path = os.path.join(user_dir, filename)
    
    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    now = datetime.utcnow().isoformat()
    db_file = db.query(File).filter(File.owner_id == current_user.id, File.filename == filename).first()
    
    if db_file:
        db_file.file_size = file_size
        db_file.updated_at = now
        db_file.last_modified_by = current_user.id
    else:
        db_file = File(
            owner_id=current_user.id,
            filename=filename,
            extension=extension,
            file_size=file_size,
            storage_path=storage_path,
            uploaded_by=current_user.id,
            last_modified_by=current_user.id
        )
        db.add(db_file)
        
    db.commit()
    return {"msg": "Upload successful"}

@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_file = db.query(File).filter(File.id == file_id, File.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(db_file.storage_path, filename=db_file.filename)

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_file = db.query(File).filter(File.id == file_id, File.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        if os.path.exists(db_file.storage_path):
            os.remove(db_file.storage_path)
    except Exception:
        pass
        
    db.delete(db_file)
    db.commit()
    return {"msg": "deleted"}

@router.get("/{file_id}/preview")
def preview_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_file = db.query(File).filter(File.id == file_id, File.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    if db_file.extension == ".py":
        try:
            with open(db_file.storage_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"type": "code", "content": content, "filename": db_file.filename}
        except Exception:
            raise HTTPException(status_code=500, detail="Could not read file")
    elif db_file.extension == ".jpg":
        return FileResponse(db_file.storage_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=400, detail="Preview not supported for this file type")

@router.post("/sync", response_model=SyncDelta)
def sync_files(manifest: SyncManifest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    server_files = db.query(File).filter(File.owner_id == current_user.id).all()
    server_map = {f.filename: f for f in server_files}
    
    client_map = {item.filename: item for item in manifest.files}
    
    to_upload = []
    to_download = []
    to_delete_local = []
    
    for fname, client_item in client_map.items():
        if fname not in server_map:
            to_upload.append(fname)
        elif server_map[fname].file_size != client_item.size:
            to_upload.append(fname)
            
    for fname, srv_file in server_map.items():
        if fname not in client_map:
            to_download.append({"id": srv_file.id, "filename": srv_file.filename})
            
    return {
        "to_upload": to_upload,
        "to_download": to_download,
        "to_delete_local": to_delete_local
    }
