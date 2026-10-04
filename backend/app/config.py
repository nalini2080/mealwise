import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://mealwise:mealwise@localhost:5433/mealwise"
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
# Used when the main model stays overloaded; set to "" to disable.
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-flash-lite-latest")

# Signs the visitor cookie so nobody can swap in another profile's id.
# Production sets a long random value; the default is for local development only.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-not-secret")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # HTTPS-only in prod

# Gemini calls are capped per rolling 24 hours so a public demo stays inside the free quota.
AI_LIMIT_PER_VISITOR = int(os.getenv("AI_LIMIT_PER_VISITOR", "15"))
AI_LIMIT_TOTAL = int(os.getenv("AI_LIMIT_TOTAL", "200"))

# Built frontend to serve from the API (single deployable app). Unset in dev,
# where Vite serves the frontend and proxies /api.
STATIC_DIR = os.getenv("STATIC_DIR")

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
