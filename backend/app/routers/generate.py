"""Grow the menu with Gemini-written recipes, validated before they are saved."""

from datetime import date

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status

from app.ai_limits import use_ai_quota
from app.db import get_conn
from app.profile import current_profile
from app.gemini import GeminiFailed, GeminiUnavailable
from app.recipe_ai import GeneratedRecipe, RecipeGenerator, RecipeRequest, get_recipe_generator
from app.routers.ingredients import resolve_labels
from app.routers.recipes import DAY_TOTALS_CTE, _query_matches
from app.schemas import GenerateRequest, GenerateResult, RejectedRecipe

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

MAX_GRAMS = 3000
MAX_STEPS = 10


class Rejected(Exception):
    """A generated recipe failed validation; the message is shown to the user."""


def _context(conn: psycopg.Connection, body: GenerateRequest,
             profile_id: int) -> tuple[RecipeRequest, dict]:
    params = {"profile_id": profile_id, "day": date.today()}
    catalog = conn.execute(
        """
        SELECT i.id, i.name, i.always_on_hand,
               EXISTS (SELECT 1 FROM profile_avoided a
                       WHERE a.profile_id = %(profile_id)s AND a.ingredient_id = i.id) AS avoided,
               EXISTS (SELECT 1 FROM pantry_items p
                       WHERE p.profile_id = %(profile_id)s AND p.ingredient_id = i.id) AS in_pantry
        FROM ingredients i ORDER BY i.name
        """,
        params,
    ).fetchall()
    remaining = conn.execute(
        f"""
        WITH {DAY_TOTALS_CTE}
        SELECT GREATEST(g.protein_g    - t.protein_g,    0) AS protein_g,
               GREATEST(g.veg_servings - t.veg_servings, 0) AS veg_servings,
               GREATEST(g.iron_mg      - t.iron_mg,      0) AS iron_mg,
               GREATEST(g.fiber_g      - t.fiber_g,      0) AS fiber_g
        FROM nutrition_goals g CROSS JOIN day_totals t
        WHERE g.profile_id = %(profile_id)s
        """,
        params,
    ).fetchone()
    titles = [r["title"] for r in conn.execute(
        "SELECT title FROM recipes WHERE created_by IS NULL OR created_by = %(profile_id)s "
        "ORDER BY title",
        params,
    )]

    request = RecipeRequest(
        count=body.count,
        allowed=[c["name"] for c in catalog if not c["avoided"]],
        pantry=[c["name"] for c in catalog if c["in_pantry"] and not c["avoided"]],
        avoid=[c["name"] for c in catalog if c["avoided"]],
        remaining={k: float(v) for k, v in remaining.items()},
        existing_titles=titles,
        meal_type=body.meal_type,
        focus=body.focus,
    )
    lookup = {
        "by_name": {c["name"]: c for c in catalog},
        "titles": {t.lower() for t in titles},
    }
    return request, lookup


def _validate(conn, recipe: GeneratedRecipe, lookup: dict) -> dict:
    """Return a clean, insert-ready recipe or raise Rejected with a reason.
    Never trust model output: names, amounts and allergies are all re-checked."""
    title = " ".join(recipe.title.split())
    if not 3 <= len(title) <= 80:
        raise Rejected("title is missing or too long")
    if title.lower() in lookup["titles"]:
        raise Rejected("a recipe with this name already exists")
    steps = [s.strip() for s in recipe.steps if s.strip()]
    if not 1 <= len(steps) <= MAX_STEPS:
        raise Rejected("needs between 1 and 10 steps")
    if not 1 <= recipe.servings <= 12 or not 1 <= recipe.total_minutes <= 300:
        raise Rejected("unrealistic servings or cooking time")
    if not 2 <= len(recipe.ingredients) <= 20:
        raise Rejected("needs between 2 and 20 ingredients")

    # Resolve names: exact catalog name first, then alias/fuzzy match (strict
    # threshold) so "chick peas" still works but a made-up item does not.
    by_name = lookup["by_name"]
    unresolved = [i.name for i in recipe.ingredients if i.name.strip().lower() not in by_name]
    fuzzy = {r["label"]: r["name"] for r in resolve_labels(conn, unresolved, threshold=0.6) if r["id"]}

    merged: dict[int, dict] = {}
    for item in recipe.ingredients:
        name = item.name.strip().lower()
        row = by_name.get(name) or by_name.get(fuzzy.get(item.name, ""))
        if row is None:
            raise Rejected(f"uses “{item.name}”, which isn't in the ingredient catalog")
        if row["avoided"]:  # allergy safety net, independent of the prompt
            raise Rejected(f"contains {row['name']}, which is on your avoid list")
        if not 0 < item.grams <= MAX_GRAMS:
            raise Rejected(f"unrealistic amount of {row['name']}")
        entry = merged.setdefault(row["id"], {"grams": 0.0, "optional": True, "row": row})
        entry["grams"] += item.grams
        entry["optional"] = entry["optional"] and item.optional  # required wins

    real = [e for e in merged.values() if not e["optional"] and not e["row"]["always_on_hand"]]
    if len(real) < 2:
        raise Rejected("needs at least two real ingredients")

    return {
        "title": title,
        "description": " ".join(recipe.description.split())[:300],
        "meal_type": recipe.meal_type,
        "servings": recipe.servings,
        "total_minutes": recipe.total_minutes,
        "steps": steps,
        "ingredient_ids": list(merged),
        "grams": [round(e["grams"], 1) for e in merged.values()],
        "optional": [e["optional"] for e in merged.values()],
    }


def _insert(conn: psycopg.Connection, recipe: dict, profile_id: int) -> int:
    recipe_id = conn.execute(
        """
        INSERT INTO recipes (title, description, meal_type, servings, total_minutes, steps,
                             source, created_by)
        VALUES (%(title)s, %(description)s, %(meal_type)s, %(servings)s, %(total_minutes)s,
                %(steps)s, 'gemini', %(profile_id)s)
        RETURNING id
        """,
        {**recipe, "profile_id": profile_id},
    ).fetchone()["id"]
    conn.execute(
        """
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, grams, is_optional)
        SELECT %(recipe_id)s, * FROM unnest(%(ingredient_ids)s::int[], %(grams)s::numeric[],
                                            %(optional)s::bool[])
        """,
        {**recipe, "recipe_id": recipe_id},
    )
    return recipe_id


@router.post("/generate", response_model=GenerateResult, status_code=status.HTTP_201_CREATED)
def generate_recipes(
    body: GenerateRequest,
    conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
    generator: RecipeGenerator = Depends(get_recipe_generator),
):
    """Ask Gemini for new recipes tailored to the pantry, today's goals and
    allergies. Valid ones are saved to your menu (only you see them); invalid
    ones are reported."""
    request, lookup = _context(conn, body, profile_id)
    use_ai_quota(conn, profile_id, "generate")
    try:
        proposals = generator.generate(request)
    except GeminiUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    except GeminiFailed as exc:
        raise HTTPException(502, str(exc)) from exc

    created_ids, rejected = [], []
    for proposal in proposals[: body.count]:
        try:
            clean = _validate(conn, proposal, lookup)
        except Rejected as reason:
            rejected.append(RejectedRecipe(title=proposal.title, reason=str(reason)))
            continue
        created_ids.append(_insert(conn, clean, profile_id))
        lookup["titles"].add(clean["title"].lower())  # no duplicates within one batch

    created = [_query_matches(conn, profile_id, recipe_id=rid, include_avoided=True)[0]
               for rid in created_ids]
    return GenerateResult(created=created, rejected=rejected)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    """Remove a Gemini recipe you don't want. Curated recipes can't be deleted,
    and recipes you've logged are kept so your meal history stays intact."""
    row = conn.execute(
        """
        SELECT r.source, EXISTS (SELECT 1 FROM meal_logs m WHERE m.recipe_id = r.id) AS logged
        FROM recipes r
        WHERE r.id = %s AND (r.created_by IS NULL OR r.created_by = %s)
        """,
        (recipe_id, profile_id),
    ).fetchone()
    if row is None:  # also hides other visitors' recipes
        raise HTTPException(404, "Recipe not found.")
    if row["source"] != "gemini":
        raise HTTPException(403, "Only Gemini-generated recipes can be removed.")
    if row["logged"]:
        raise HTTPException(409, "You've logged this recipe, so it's kept for your meal history.")
    conn.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
