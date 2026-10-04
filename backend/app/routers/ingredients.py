import psycopg
from fastapi import APIRouter, Depends, Query

from app.db import get_conn
from app.schemas import Ingredient

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

# Searches canonical names and aliases together. Prefix matches rank first,
# then trigram similarity handles typos ("brocoli") and plurals.
SEARCH_SQL = """
WITH candidates AS (
    SELECT id AS ingredient_id, name AS term FROM ingredients
    UNION ALL
    SELECT ingredient_id, alias FROM ingredient_aliases
),
scored AS (
    SELECT ingredient_id,
           MAX(CASE WHEN term ILIKE %(q)s || '%%' THEN 2
                    WHEN term ILIKE '%%' || %(q)s || '%%' THEN 1
                    ELSE 0 END + similarity(term, %(q)s)) AS score
    FROM candidates
    WHERE term ILIKE '%%' || %(q)s || '%%' OR similarity(term, %(q)s) > 0.3
    GROUP BY ingredient_id
)
SELECT i.id, i.name, i.category
FROM scored s
JOIN ingredients i ON i.id = s.ingredient_id
WHERE NOT i.always_on_hand
ORDER BY s.score DESC, i.name
LIMIT %(limit)s
"""

# Maps free-text labels (e.g. from the photo model) to catalog ingredients in a
# single round trip: unnest the labels and pick each one's best match with LATERAL.
RESOLVE_SQL = """
SELECT q.label, m.id, m.name
FROM unnest(%(labels)s::text[]) WITH ORDINALITY AS q(label, pos)
LEFT JOIN LATERAL (
    SELECT i.id, i.name
    FROM (
        SELECT id AS ingredient_id, similarity(name, lower(q.label)) AS score FROM ingredients
        UNION ALL
        SELECT ingredient_id, similarity(alias, lower(q.label)) FROM ingredient_aliases
    ) c
    JOIN ingredients i ON i.id = c.ingredient_id
    WHERE c.score >= %(threshold)s AND NOT i.always_on_hand
    ORDER BY c.score DESC
    LIMIT 1
) m ON true
ORDER BY q.pos
"""


def resolve_labels(
    conn: psycopg.Connection, labels: list[str], threshold: float = 0.4
) -> list[dict]:
    """Return [{label, id, name}] in input order; id/name are None when unmatched."""
    if not labels:
        return []
    return conn.execute(RESOLVE_SQL, {"labels": labels, "threshold": threshold}).fetchall()


@router.get("", response_model=list[Ingredient])
def search_ingredients(
    q: str = Query(min_length=1, max_length=60),
    limit: int = Query(default=8, ge=1, le=25),
    conn: psycopg.Connection = Depends(get_conn),
):
    return conn.execute(SEARCH_SQL, {"q": q.strip().lower(), "limit": limit}).fetchall()


@router.get("/common", response_model=list[Ingredient])
def common_ingredients(conn: psycopg.Connection = Depends(get_conn)):
    """Staples shown on the quick-add checklist."""
    return conn.execute(
        "SELECT id, name, category FROM ingredients WHERE is_common ORDER BY category, name"
    ).fetchall()
