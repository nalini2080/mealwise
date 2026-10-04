import psycopg
from fastapi import APIRouter, Depends

from app.config import DEFAULT_PROFILE_ID
from app.db import get_conn
from app.schemas import Goals

router = APIRouter(prefix="/api/goals", tags=["goals"])

GOAL_COLUMNS = "kcal, protein_g, veg_servings, fiber_g, iron_mg"


@router.get("", response_model=Goals)
def get_goals(conn: psycopg.Connection = Depends(get_conn)):
    return conn.execute(
        f"SELECT {GOAL_COLUMNS} FROM nutrition_goals WHERE profile_id = %s",
        (DEFAULT_PROFILE_ID,),
    ).fetchone()


@router.put("", response_model=Goals)
def update_goals(goals: Goals, conn: psycopg.Connection = Depends(get_conn)):
    return conn.execute(
        f"""
        INSERT INTO nutrition_goals (profile_id, {GOAL_COLUMNS})
        VALUES (%(profile_id)s, %(kcal)s, %(protein_g)s, %(veg_servings)s, %(fiber_g)s, %(iron_mg)s)
        ON CONFLICT (profile_id) DO UPDATE SET
            kcal = EXCLUDED.kcal, protein_g = EXCLUDED.protein_g,
            veg_servings = EXCLUDED.veg_servings, fiber_g = EXCLUDED.fiber_g,
            iron_mg = EXCLUDED.iron_mg, updated_at = now()
        RETURNING {GOAL_COLUMNS}
        """,
        {"profile_id": DEFAULT_PROFILE_ID, **goals.model_dump()},
    ).fetchone()
