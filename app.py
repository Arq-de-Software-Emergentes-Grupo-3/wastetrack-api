from fastapi import FastAPI
from routes.container import container
from routes.auth import auth
from routes.user import user
from config.db import engine, Base

import models.container
import models.user

app = FastAPI(
    title="Waste Track",
    version="0.0.1",
)

Base.metadata.create_all(bind=engine)

app.include_router(auth, prefix="/api/v1")
app.include_router(user, prefix="/api/v1")
app.include_router(container, prefix="/api/v1")
