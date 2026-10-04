from datetime import date

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import DEFAULT_PROFILE_ID
from app.db import get_conn
from app.schemas import MealType, RecipeDetail, RecipeMatch, ShoppingItem

router = APIRouter(prefix="/api", tags=["recipes"])

NUTRIENTS = ("kcal", "protein_g", "carbs_g", "fat_g", "fiber_g", "iron_mg", "veg_servings")

# Totals eaten on a given day; reused by the meals router.
DAY_TOTALS_CTE = """
day_totals AS (
    SELECT
        COALESCE(SUM(n.kcal         * m.servings), 0) AS kcal,
        COALESCE(SUM(n.protein_g    * m.servings), 0) AS protein_g,
        COALESCE(SUM(n.carbs_g      * m.servings), 0) AS carbs_g,
        COALESCE(SUM(n.fat_g        * m.servings), 0) AS fat_g,
        COALESCE(SUM(n.fiber_g      * m.servings), 0) AS fiber_g,
        COALESCE(SUM(n.iron_mg      * m.servings), 0) AS iron_mg,
        COALESCE(SUM(n.veg_servings * m.servings), 0) AS veg_servings
    FROM meal_logs m
    JOIN recipe_nutrition n ON n.recipe_id = m.recipe_id
    WHERE m.profile_id = %(profile_id)s AND m.eaten_on = %(day)s
)"""

# 1. have      - what's in the pantry, plus basics like salt that are always on hand
# 2. avoid     - ingredients blocked by your allergies or avoided-foods list
# 3. coverage  - per recipe: required ingredient count, how many you have, what's
#                missing, and any required ingredient you must avoid (conflicts)
# 4. remaining - today's goals minus what's already been eaten
# 5. score     - each serving's share of the remaining gap (capped at 100% per nutrient),
#                weighted toward protein and veggies; nutrients already met count as covered
MATCH_SQL = f"""
WITH have AS (
    SELECT ingredient_id FROM pantry_items WHERE profile_id = %(profile_id)s
    UNION
    SELECT id FROM ingredients WHERE always_on_hand
),
avoid AS (
    SELECT ingredient_id FROM profile_avoided WHERE profile_id = %(profile_id)s
),
coverage AS (
    SELECT
        ri.recipe_id,
        COUNT(*) AS total_count,
        COUNT(h.ingredient_id) AS have_count,
        COALESCE(ARRAY_AGG(i.name ORDER BY i.name) FILTER (WHERE h.ingredient_id IS NULL),
                 ARRAY[]::text[]) AS missing,
        COALESCE(ARRAY_AGG(i.name ORDER BY i.name) FILTER (WHERE a.ingredient_id IS NOT NULL),
                 ARRAY[]::text[]) AS conflicts
    FROM recipe_ingredients ri
    JOIN ingredients i ON i.id = ri.ingredient_id
    LEFT JOIN have h   ON h.ingredient_id = ri.ingredient_id
    LEFT JOIN avoid a  ON a.ingredient_id = ri.ingredient_id
    WHERE NOT ri.is_optional
    GROUP BY ri.recipe_id
),
{DAY_TOTALS_CTE},
remaining AS (
    SELECT
        GREATEST(g.protein_g    - t.protein_g,    0) AS protein_g,
        GREATEST(g.veg_servings - t.veg_servings, 0) AS veg_servings,
        GREATEST(g.fiber_g      - t.fiber_g,      0) AS fiber_g,
        GREATEST(g.iron_mg      - t.iron_mg,      0) AS iron_mg
    FROM nutrition_goals g CROSS JOIN day_totals t
    WHERE g.profile_id = %(profile_id)s
)
SELECT
    r.id, r.title, r.description, r.meal_type, r.servings, r.total_minutes, r.source,
    t.tags, c.missing, c.conflicts, c.have_count, c.total_count,
    n.kcal, n.protein_g, n.carbs_g, n.fat_g, n.fiber_g, n.iron_mg, n.veg_servings,
    ROUND(100 * (
          0.35 * COALESCE(LEAST(n.protein_g    / NULLIF(rem.protein_g,    0), 1), 1)
        + 0.35 * COALESCE(LEAST(n.veg_servings / NULLIF(rem.veg_servings, 0), 1), 1)
        + 0.15 * COALESCE(LEAST(n.fiber_g      / NULLIF(rem.fiber_g,      0), 1), 1)
        + 0.15 * COALESCE(LEAST(n.iron_mg      / NULLIF(rem.iron_mg,      0), 1), 1)
    ))::int AS goal_score
FROM recipes r
JOIN coverage c         ON c.recipe_id = r.id
JOIN recipe_nutrition n ON n.recipe_id = r.id
JOIN recipe_tags t      ON t.recipe_id = r.id
CROSS JOIN remaining rem
WHERE (%(recipe_id)s::int IS NULL OR r.id = %(recipe_id)s)
  AND (%(meal_type)s::meal_type IS NULL OR r.meal_type = %(meal_type)s)
  AND (%(tag)s::text IS NULL OR %(tag)s = ANY(t.tags))
  AND cardinality(c.missing) <= %(max_missing)s
  AND (%(include_avoided)s OR cardinality(c.conflicts) = 0)
ORDER BY {{order_by}}
"""

ORDERINGS = {
    "missing": "cardinality(c.missing), goal_score DESC, r.title",
    "goals": "goal_score DESC, cardinality(c.missing), r.title",
}


def _to_match(row: dict) -> dict:
    row["nutrition"] = {k: row.pop(k) for k in NUTRIENTS}
    return row


def _query_matches(conn, *, recipe_id=None, meal_type=None, tag=None, max_missing=99,
                   sort="missing", day=None, include_avoided=False) -> list[dict]:
    sql = MATCH_SQL.format(order_by=ORDERINGS[sort])
    rows = conn.execute(sql, {
        "profile_id": DEFAULT_PROFILE_ID, "recipe_id": recipe_id, "meal_type": meal_type,
        "tag": tag, "max_missing": max_missing, "day": day or date.today(),
        "include_avoided": include_avoided,
    }).fetchall()
    return [_to_match(row) for row in rows]


@router.get("/recipes/matches", response_model=list[RecipeMatch])
def match_recipes(
    max_missing: int = Query(default=3, ge=0, le=20),
    meal_type: MealType | None = None,
    tag: str | None = None,
    sort: str = Query(default="missing", pattern="^(missing|goals)$"),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Recipes ranked by how few ingredients you're missing, then by goal fit.
    Recipes that need anything on your allergies/avoid list are never returned."""
    return _query_matches(conn, meal_type=meal_type, tag=tag,
                          max_missing=max_missing, sort=sort)


@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, conn: psycopg.Connection = Depends(get_conn)):
    # Detail still opens for an avoided recipe (e.g. one logged before an allergy
    # was added), but `conflicts` and per-ingredient `avoid` flags make it explicit.
    matches = _query_matches(conn, recipe_id=recipe_id, include_avoided=True)
    if not matches:
        raise HTTPException(404, "Recipe not found.")
    recipe = matches[0]
    recipe["steps"] = conn.execute(
        "SELECT steps FROM recipes WHERE id = %s", (recipe_id,)
    ).fetchone()["steps"]
    recipe["ingredients"] = conn.execute(
        """
        SELECT i.id AS ingredient_id, i.name, ri.grams, ri.is_optional,
               (i.always_on_hand OR p.ingredient_id IS NOT NULL) AS have,
               (a.ingredient_id IS NOT NULL) AS avoid
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        LEFT JOIN pantry_items p
               ON p.ingredient_id = i.id AND p.profile_id = %(profile_id)s
        LEFT JOIN profile_avoided a
               ON a.ingredient_id = i.id AND a.profile_id = %(profile_id)s
        WHERE ri.recipe_id = %(recipe_id)s
        ORDER BY ri.is_optional, ri.grams DESC
        """,
        {"profile_id": DEFAULT_PROFILE_ID, "recipe_id": recipe_id},
    ).fetchall()
    return recipe


@router.get("/shopping-list", response_model=list[ShoppingItem])
def shopping_list(
    recipe_ids: list[int] = Query(min_length=1, max_length=20),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Everything missing for the chosen recipes, combined across recipes.
    Never lists an ingredient on your allergies/avoid list."""
    return conn.execute(
        """
        SELECT i.id AS ingredient_id, i.name, i.category,
               SUM(ri.grams) AS grams,
               ARRAY_AGG(r.title ORDER BY r.title) AS for_recipes
        FROM recipe_ingredients ri
        JOIN recipes r     ON r.id = ri.recipe_id
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = ANY(%(recipe_ids)s)
          AND NOT ri.is_optional
          AND NOT i.always_on_hand
          AND NOT EXISTS (
              SELECT 1 FROM pantry_items p
              WHERE p.profile_id = %(profile_id)s AND p.ingredient_id = i.id
          )
          AND NOT EXISTS (
              SELECT 1 FROM profile_avoided a
              WHERE a.profile_id = %(profile_id)s AND a.ingredient_id = i.id
          )
        GROUP BY i.id, i.name, i.category
        ORDER BY i.category, i.name
        """,
        {"recipe_ids": recipe_ids, "profile_id": DEFAULT_PROFILE_ID},
    ).fetchall()
