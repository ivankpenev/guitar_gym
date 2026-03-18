"""Guitar Gym — FastAPI application entry point."""

from fastapi import FastAPI

from app.routers import auth, exercises, progress

app = FastAPI(
    title="Guitar Gym API",
    description="Backend for the Guitar Gym practice app",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(exercises.router)
app.include_router(progress.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
