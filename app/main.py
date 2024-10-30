from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.queries import query_router

app = FastAPI()

origins = [
    "http://localhost", # for development
    "http://127.0.0.1", # for development
]

app.add_middleware(
    CORSMiddleware, # Cross-Origin Resource Sharing
    allow_origins=["*"],  # allow all origins
    allow_credentials=True, # allow credentials
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
)

app.include_router(query_router)
