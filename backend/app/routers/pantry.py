import psycopg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_BYTES
from app.ai_limits import use_ai_quota
from app.db import get_conn
from app.profile import current_profile
from app.routers.ingredients import resolve_labels
from app.schemas import DetectedIngredient, PantryAdd, PantryItem, ScanResult
from app.gemini import GeminiFailed, GeminiUnavailable
from app.vision import IngredientDetector, get_detector

router = APIRouter(prefix="/api/pantry", tags=["pantry"])

LIST_SQL = """
SELECT p.ingredient_id, i.name, i.category, p.source, p.added_at
FROM pantry_items p
JOIN ingredients i ON i.id = p.ingredient_id
WHERE p.profile_id = %s
ORDER BY i.category, i.name
"""


@router.get("", response_model=list[PantryItem])
def list_pantry(conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    return conn.execute(LIST_SQL, (profile_id,)).fetchall()


@router.post("", response_model=list[PantryItem], status_code=status.HTTP_201_CREATED)
def add_to_pantry(body: PantryAdd, conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    """Add ingredients; re-adding an existing one is a no-op (idempotent)."""
    found = conn.execute(
        "SELECT id FROM ingredients WHERE id = ANY(%s)", (body.ingredient_ids,)
    ).fetchall()
    unknown = set(body.ingredient_ids) - {row["id"] for row in found}
    if unknown:
        raise HTTPException(404, f"Unknown ingredient ids: {sorted(unknown)}")

    conn.execute(
        """
        INSERT INTO pantry_items (profile_id, ingredient_id, source)
        SELECT %s, unnest(%s::int[]), %s
        ON CONFLICT (profile_id, ingredient_id) DO NOTHING
        """,
        (profile_id, body.ingredient_ids, body.source),
    )
    return conn.execute(LIST_SQL, (profile_id,)).fetchall()


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_pantry(ingredient_id: int, conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    deleted = conn.execute(
        "DELETE FROM pantry_items WHERE profile_id = %s AND ingredient_id = %s",
        (profile_id, ingredient_id),
    ).rowcount
    if not deleted:
        raise HTTPException(404, "That ingredient is not in your pantry.")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_pantry(conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
):
    conn.execute("DELETE FROM pantry_items WHERE profile_id = %s", (profile_id,))


@router.post("/scan", response_model=ScanResult)
def scan_photo(
    photo: UploadFile = File(...),
    conn: psycopg.Connection = Depends(get_conn),
    profile_id: int = Depends(current_profile),
    detector: IngredientDetector = Depends(get_detector),
):
    """Detect ingredients in a photo. Nothing is saved: the user reviews the
    list in the UI and confirms via POST /api/pantry with source="photo".

    A plain `def` on purpose: FastAPI runs it in a worker thread, so the slow
    model call (and its retries) never blocks other requests."""
    if photo.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(415, "Please upload a JPEG, PNG, WebP or HEIC image.")
    image = photo.file.read(MAX_UPLOAD_BYTES + 1)
    if len(image) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image is too large (max 8 MB).")
    if not image:
        raise HTTPException(400, "The uploaded file is empty.")

    use_ai_quota(conn, profile_id, "scan")
    vocabulary = [
        row["name"]
        for row in conn.execute("SELECT name FROM ingredients WHERE NOT always_on_hand")
    ]
    try:
        items = detector.detect(image, photo.content_type, vocabulary)
    except GeminiUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    except GeminiFailed as exc:
        raise HTTPException(502, str(exc)) from exc

    confidence = {item.name: item.confidence for item in items}
    detected, unmatched, seen = [], [], set()
    for row in resolve_labels(conn, [item.name for item in items]):
        if row["id"] is None:
            unmatched.append(row["label"])
        elif row["id"] not in seen:  # two labels can map to one ingredient
            seen.add(row["id"])
            detected.append(
                DetectedIngredient(
                    label=row["label"],
                    ingredient_id=row["id"],
                    name=row["name"],
                    confidence=confidence[row["label"]],
                )
            )
    return ScanResult(detected=detected, unmatched=unmatched)
