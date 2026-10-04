from datetime import date

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db import get_conn
from app.profile import current_profile
from app.routers.goals import GOAL_COLUMNS
from app.routers.recipes import DAY_TOTALS_CTE, NUTRIENTS
from app.schemas import DaySummary, MealLog, MealLogIn

router = APIRouter(prefix="/api/meals", tags=["meals"])

MEALS_SQL = """
SELECT m.id, m.recipe_id, r.title, r.meal_type, m.servings,
       n.kcal * m.servings         AS kcal,
       n.protein_g * m.servings    AS protein_g,
       n.carbs_g * m.servings      AS carbs_g,
       n.fat_g * m.servings        AS fat_g,
       n.fiber_g * m.servings      AS fiber_g,
       n.iron_mg * m.servings      AS iron_mg,
       n.veg_servings * m.servings AS veg_servings
FROM meal_logs m
JOIN recipes r          ON r.id = m.recipe_id
JOIN recipe_nutrition n ON n.recipe_id = m.recipe_id
WHERE m.profile_id = %(profile_id)s AND m.eaten_on = %(day)s
ORDER BY m.created_at
"""


def _nest(row: dict) -> dict:
    row["nutrition"] = {k: row.pop(k) for k in NUTRIENTS}
    return row


@router.get("", response_model=DaySummary)
def day_summary(
    day: date | None = Query(default=None, description="Defaults to today"),
    conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    """Everything logged for a day, with totals to compare against goals."""
    params = {"profile_id": profile_id, "day": day or date.today()}
    goals = conn.execute(
        f"SELECT {GOAL_COLUMNS} FROM nutrition_goals WHERE profile_id = %(profile_id)s", params
    ).fetchone()
    totals = conn.execute(f"WITH {DAY_TOTALS_CTE} SELECT * FROM day_totals", params).fetchone()
    meals = [_nest(row) for row in conn.execute(MEALS_SQL, params).fetchall()]
    return {"day": params["day"], "goals": goals, "totals": totals, "meals": meals}


@router.post("", response_model=MealLog, status_code=status.HTTP_201_CREATED)
def log_meal(body: MealLogIn, conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    if not conn.execute(
        "SELECT 1 FROM recipes WHERE id = %s AND (created_by IS NULL OR created_by = %s)",
        (body.recipe_id, profile_id),
    ).fetchone():
        raise HTTPException(404, "Recipe not found.")
    day = body.eaten_on or date.today()
    meal_id = conn.execute(
        """
        INSERT INTO meal_logs (profile_id, recipe_id, servings, eaten_on)
        VALUES (%s, %s, %s, %s) RETURNING id
        """,
        (profile_id, body.recipe_id, body.servings, day),
    ).fetchone()["id"]
    rows = conn.execute(MEALS_SQL, {"profile_id": profile_id, "day": day}).fetchall()
    return _nest(next(row for row in rows if row["id"] == meal_id))


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    deleted = conn.execute(
        "DELETE FROM meal_logs WHERE id = %s AND profile_id = %s",
        (meal_id, profile_id),
    ).rowcount
    if not deleted:
        raise HTTPException(404, "Meal log not found.")
