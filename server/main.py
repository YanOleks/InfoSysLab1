import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers.auth_router import router as auth_router
from routers.files_router import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    os.makedirs("storage", exist_ok=True)
    yield

app = FastAPI(title="File Manager API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(files_router, prefix="/files", tags=["files"])
