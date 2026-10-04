from collections.abc import Iterator
from pathlib import Path

import psycopg
from fastapi import Request
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import DATABASE_URL, ROOT_DIR

SQL_FILES = ["schema.sql", "seed_ingredients.sql", "seed_recipes.sql"]


def create_pool(url: str = DATABASE_URL) -> ConnectionPool:
    return ConnectionPool(url, open=True, kwargs={"row_factory": dict_row}, min_size=1, max_size=10)


def get_conn(request: Request) -> Iterator[psycopg.Connection]:
    """FastAPI dependency: one pooled connection per request.
    Commits when the request succeeds, rolls back if it raises."""
    with request.app.state.pool.connection() as conn:
        yield conn


def ensure_database(url: str = DATABASE_URL) -> bool:
    """Create and seed the schema only if it doesn't exist yet (safe on every
    deploy: existing data is never touched). Returns True if it initialized."""
    with psycopg.connect(url) as conn:
        exists = conn.execute("SELECT to_regclass('public.recipes') IS NOT NULL").fetchone()[0]
    if not exists:
        reset_database(url)
    return not exists


def reset_database(url: str = DATABASE_URL, sql_dir: Path = ROOT_DIR / "db") -> None:
    """Drop and recreate every table, then load the seed data, in one transaction."""
    with psycopg.connect(url) as conn:
        for name in SQL_FILES:
            conn.execute((sql_dir / name).read_text())
