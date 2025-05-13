from fastapi import FastAPI
from routes import *

app = FastAPI(
	title="Waste Track",
	version="0.0.1",	
)

#app.include_router(user.router)