import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.db import create_pool, ensure_database
from app.routers import allergies, generate, goals, ingredients, meals, pantry, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    if ensure_database():
        logging.getLogger("uvicorn.error").info("Created schema and loaded seed data")
    app.state.pool = create_pool()
    yield
    app.state.pool.close()


app = FastAPI(
    title="MealWise API",
    description="Meals from what you have, tailored to what your body needs.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (ingredients, pantry, recipes, generate, goals, meals, allergies):
    app.include_router(module.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}


# In production one service serves both the API and the built React app.
# Mounted last so every /api route above takes priority.
if STATIC_DIR and Path(STATIC_DIR).is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
