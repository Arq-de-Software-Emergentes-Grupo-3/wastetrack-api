from fastapi import FastAPI
from routes.container import container
from config.db import engine
from models.container import Base

app = FastAPI(
    title="Waste Track",
    version="0.0.1",
)

# Crear todas las tablas registradas
Base.metadata.create_all(bind=engine)

app.include_router(container, prefix="/api/v1")
