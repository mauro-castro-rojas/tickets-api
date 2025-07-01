from typing import Type

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.conf.config import get_app_settings
from app.routers.v1.api_router import router as root_api_router
from app.conf.settings.dependencies import validate_api_key

from app.utils.logger import log
load_dotenv()
app_settings = get_app_settings()

app = FastAPI(
    title=app_settings.project_name,
)

@app.get("/health")
def health():
    return {"status": "ok"}


# CORS Related Code
# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "http://localhost:8000",
#     "http://localhost:8080",
# ]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)


# API Related Code
app.include_router(root_api_router, prefix=app_settings.api_v1_str)
