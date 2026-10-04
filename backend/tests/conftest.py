import os

import psycopg
import pytest

# Point the app at a throwaway database *before* app modules read config.
ADMIN_URL = os.getenv("TEST_ADMIN_URL", "postgresql://mealwise:mealwise@localhost:5433/postgres")
TEST_DB = "mealwise_test"
os.environ["DATABASE_URL"] = ADMIN_URL.rsplit("/", 1)[0] + f"/{TEST_DB}"

from fastapi.testclient import TestClient  # noqa: E402

from app.config import DATABASE_URL  # noqa: E402
from app.db import reset_database  # noqa: E402
from app.main import app  # noqa: E402
from app.recipe_ai import get_recipe_generator  # noqa: E402
from app.vision import VisionItem, get_detector  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def test_database():
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
        conn.execute(f"CREATE DATABASE {TEST_DB}")
    reset_database(DATABASE_URL)
    yield


@pytest.fixture(autouse=True)
def clean_state():
    """Each test starts with an empty pantry, no meals, no allergies and default goals."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("TRUNCATE pantry_items, meal_logs, profile_allergens, profile_avoided_ingredients")
        conn.execute("DELETE FROM recipes WHERE source = 'gemini'")
        conn.execute(
            "UPDATE nutrition_goals SET kcal=2000, protein_g=90, veg_servings=5, "
            "fiber_g=28, iron_mg=18 WHERE profile_id = 1"
        )
    yield


class FakeDetector:
    def __init__(self, items=None, error=None):
        self.items = items or []
        self.error = error
        self.calls = []

    def detect(self, image, mime_type, vocabulary):
        self.calls.append((image, mime_type, vocabulary))
        if self.error:
            raise self.error
        return [VisionItem(name=n, confidence=c) for n, c in self.items]


@pytest.fixture
def fake_detector():
    detector = FakeDetector()
    app.dependency_overrides[get_detector] = lambda: detector
    yield detector
    app.dependency_overrides.pop(get_detector, None)


class FakeRecipeGenerator:
    def __init__(self):
        self.recipes = []
        self.error = None
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.recipes


@pytest.fixture
def fake_generator():
    generator = FakeRecipeGenerator()
    app.dependency_overrides[get_recipe_generator] = lambda: generator
    yield generator
    app.dependency_overrides.pop(get_recipe_generator, None)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def ids(client):
    """Look up ingredient ids by name: ids("eggs", "spinach") -> [..]."""
    with psycopg.connect(DATABASE_URL) as conn:
        lookup = dict(conn.execute("SELECT name, id FROM ingredients").fetchall())
    return lambda *names: [lookup[n] for n in names]


@pytest.fixture
def recipe_id():
    with psycopg.connect(DATABASE_URL) as conn:
        lookup = dict(conn.execute("SELECT title, id FROM recipes").fetchall())
    return lookup.__getitem__
