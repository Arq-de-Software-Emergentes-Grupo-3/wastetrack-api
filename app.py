from fastapi import FastAPI
from routes.container import container
from routes.auth import auth
from routes.user import user
from config.db import engine, Base
from fastapi.middleware.cors import CORSMiddleware

import models.container
import models.user
import uvicorn
import os

app = FastAPI(
    title="Waste Track",
    version="0.0.1",
)
origins = [
    "http://localhost:3000",
    "https://waste-track.netlify.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth, prefix="/api/v1")
app.include_router(user, prefix="/api/v1")
app.include_router(container, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
