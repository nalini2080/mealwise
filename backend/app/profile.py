"""Anonymous per-visitor profiles, tracked with a signed cookie.

The first request from a browser creates a profile (with default goals) and
sets `mw_profile=<id>.<hmac>`. The HMAC means a visitor can't edit the cookie
to read someone else's pantry; an invalid or stale cookie just gets a fresh profile.
"""

import hashlib
import hmac

import psycopg
from fastapi import Depends, Request, Response

from app.config import COOKIE_SECURE, SECRET_KEY
from app.db import get_conn

COOKIE_NAME = "mw_profile"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def _sign(profile_id: int) -> str:
    digest = hmac.new(SECRET_KEY.encode(), str(profile_id).encode(), hashlib.sha256).hexdigest()
    return f"{profile_id}.{digest}"


def _verify(cookie: str | None) -> int | None:
    if not cookie or "." not in cookie:
        return None
    raw_id, _ = cookie.split(".", 1)
    if not raw_id.isdigit() or not hmac.compare_digest(_sign(int(raw_id)), cookie):
        return None
    return int(raw_id)


def current_profile(
    request: Request,
    response: Response,
    conn: psycopg.Connection = Depends(get_conn),
) -> int:
    """FastAPI dependency returning the visitor's profile id, creating one if needed."""
    profile_id = _verify(request.cookies.get(COOKIE_NAME))
    if profile_id is not None and conn.execute(
        "SELECT 1 FROM profiles WHERE id = %s", (profile_id,)
    ).fetchone():
        return profile_id

    profile_id = conn.execute(
        "INSERT INTO profiles (name) VALUES ('Guest') RETURNING id"
    ).fetchone()["id"]
    conn.execute("INSERT INTO nutrition_goals (profile_id) VALUES (%s)", (profile_id,))
    response.set_cookie(
        COOKIE_NAME, _sign(profile_id), max_age=COOKIE_MAX_AGE,
        httponly=True, samesite="lax", secure=COOKIE_SECURE,
    )
    return profile_id
