import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.config import DEFAULT_PROFILE_ID
from app.db import get_conn
from app.schemas import Allergies, AllergiesUpdate

router = APIRouter(prefix="/api/allergies", tags=["allergies"])


def _load(conn: psycopg.Connection) -> dict:
    params = {"profile_id": DEFAULT_PROFILE_ID}
    selected = conn.execute(
        "SELECT allergen FROM profile_allergens WHERE profile_id = %(profile_id)s ORDER BY allergen",
        params,
    ).fetchall()
    avoided = conn.execute(
        """
        SELECT i.id, i.name, i.category
        FROM profile_avoided_ingredients p JOIN ingredients i ON i.id = p.ingredient_id
        WHERE p.profile_id = %(profile_id)s
        ORDER BY i.name
        """,
        params,
    ).fetchall()
    # Every allergen with a few example ingredients from the catalog, so the UI
    # can show what each group covers without hard-coding it.
    options = conn.execute(
        """
        SELECT a.allergen AS key,
               COALESCE(ARRAY_AGG(i.name ORDER BY i.name) FILTER (WHERE i.id IS NOT NULL),
                        ARRAY[]::text[]) AS examples
        FROM unnest(enum_range(NULL::allergen)) AS a(allergen)
        LEFT JOIN ingredient_allergens ia ON ia.allergen = a.allergen
        LEFT JOIN ingredients i ON i.id = ia.ingredient_id
        GROUP BY a.allergen
        ORDER BY a.allergen
        """
    ).fetchall()
    hidden = conn.execute(
        """
        SELECT COUNT(DISTINCT ri.recipe_id) AS n
        FROM recipe_ingredients ri
        JOIN profile_avoided pa
          ON pa.ingredient_id = ri.ingredient_id AND pa.profile_id = %(profile_id)s
        WHERE NOT ri.is_optional
        """,
        params,
    ).fetchone()["n"]
    return {
        "allergens": [row["allergen"] for row in selected],
        "avoided_ingredients": avoided,
        "options": options,
        "hidden_recipe_count": hidden,
    }


@router.get("", response_model=Allergies)
def get_allergies(conn: psycopg.Connection = Depends(get_conn)):
    return _load(conn)


@router.put("", response_model=Allergies)
def update_allergies(body: AllergiesUpdate, conn: psycopg.Connection = Depends(get_conn)):
    """Replace the full set in one transaction (simpler and safer for the UI
    than diffing individual adds/removes)."""
    ids = sorted(set(body.avoided_ingredient_ids))
    found = conn.execute("SELECT id FROM ingredients WHERE id = ANY(%s)", (ids,)).fetchall()
    unknown = set(ids) - {row["id"] for row in found}
    if unknown:
        raise HTTPException(404, f"Unknown ingredient ids: {sorted(unknown)}")

    params = {"profile_id": DEFAULT_PROFILE_ID, "allergens": sorted(set(body.allergens)), "ids": ids}
    conn.execute("DELETE FROM profile_allergens WHERE profile_id = %(profile_id)s", params)
    conn.execute("DELETE FROM profile_avoided_ingredients WHERE profile_id = %(profile_id)s", params)
    conn.execute(
        """
        INSERT INTO profile_allergens (profile_id, allergen)
        SELECT %(profile_id)s, unnest(%(allergens)s::allergen[])
        """,
        params,
    )
    conn.execute(
        """
        INSERT INTO profile_avoided_ingredients (profile_id, ingredient_id)
        SELECT %(profile_id)s, unnest(%(ids)s::int[])
        """,
        params,
    )
    return _load(conn)
