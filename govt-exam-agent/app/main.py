from fastapi import FastAPI
from app.api.routes import router
from app.db import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Server running"}