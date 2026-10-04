from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_pool
from app.routers import allergies, generate, goals, ingredients, meals, pantry, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
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
