from fastapi import FastAPI

from app.database import Base, engine
from app.routers import tasks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="A task management REST API for teams",
    version="0.1.0",
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
