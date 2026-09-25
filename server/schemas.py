from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class FileMetadata(BaseModel):
    id: int
    filename: str
    extension: str
    file_size: int
    created_at: str
    updated_at: str
    uploaded_by_username: str
    last_modified_by_username: str

    class Config:
        from_attributes = True

class SyncManifestItem(BaseModel):
    filename: str
    size: int

class SyncManifest(BaseModel):
    files: list[SyncManifestItem]

class SyncDelta(BaseModel):
    to_upload: list[str]       
    to_download: list[dict]    
    to_delete_local: list[str] 
