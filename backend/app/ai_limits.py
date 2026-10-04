"""Daily caps on Gemini calls, so a public demo stays inside the free API quota.

Each call is recorded in ai_requests; limits are checked over a rolling 24 hours,
per visitor and across everyone.
"""

import psycopg
from fastapi import HTTPException

from app.config import AI_LIMIT_PER_VISITOR, AI_LIMIT_TOTAL


def use_ai_quota(conn: psycopg.Connection, profile_id: int, kind: str) -> None:
    """Raise 429 if a limit is reached; otherwise record this call.
    The insert commits with the request, so calls that error out aren't counted."""
    usage = conn.execute(
        """
        SELECT COUNT(*) FILTER (WHERE profile_id = %(profile_id)s) AS mine,
               COUNT(*) AS everyone
        FROM ai_requests
        WHERE created_at > now() - interval '24 hours'
        """,
        {"profile_id": profile_id},
    ).fetchone()
    if usage["everyone"] >= AI_LIMIT_TOTAL:
        raise HTTPException(
            429, "The demo has used today's AI allowance. Typing and the checklist still work; "
                 "AI features come back tomorrow."
        )
    if usage["mine"] >= AI_LIMIT_PER_VISITOR:
        raise HTTPException(
            429, f"You've used your {AI_LIMIT_PER_VISITOR} AI requests for today. "
                 "Everything else still works."
        )
    conn.execute(
        "INSERT INTO ai_requests (profile_id, kind) VALUES (%s, %s)", (profile_id, kind)
    )
