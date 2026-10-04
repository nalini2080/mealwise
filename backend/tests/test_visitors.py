"""Public-demo safety: each browser is its own private profile, and AI use is capped."""

import pytest
from fastapi.testclient import TestClient

from app import ai_limits
from app.main import app
from app.profile import COOKIE_NAME
from tests.test_generate import recipe

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


@pytest.fixture
def other_visitor():
    with TestClient(app) as c:
        yield c


def test_first_visit_sets_a_signed_httponly_cookie(client):
    res = client.get("/api/goals")
    cookie = res.headers["set-cookie"]
    assert cookie.startswith(f"{COOKIE_NAME}=") and "HttpOnly" in cookie
    assert res.json()["protein_g"] == 90  # new profiles start with default goals
    # Later requests reuse it instead of creating another profile.
    assert "set-cookie" not in client.get("/api/goals").headers


def test_visitors_have_separate_pantries_goals_and_allergies(client, other_visitor, ids):
    client.post("/api/pantry", json={"ingredient_ids": ids("eggs"), "source": "typed"})
    client.put("/api/goals", json={"kcal": 2400, "protein_g": 120, "veg_servings": 6,
                                   "fiber_g": 30, "iron_mg": 18})
    client.put("/api/allergies", json={"allergens": ["dairy"]})

    assert other_visitor.get("/api/pantry").json() == []
    assert other_visitor.get("/api/goals").json()["protein_g"] == 90
    assert other_visitor.get("/api/allergies").json()["allergens"] == []


def test_tampered_cookie_gets_a_fresh_profile_not_someone_elses(client, other_visitor, ids):
    client.post("/api/pantry", json={"ingredient_ids": ids("eggs"), "source": "typed"})
    victim_id = client.cookies[COOKIE_NAME].split(".")[0]

    res = other_visitor.get("/api/pantry", headers={"Cookie": f"{COOKIE_NAME}={victim_id}.forged"})
    assert res.json() == []
    new_id = res.headers["set-cookie"].split("=", 1)[1].split(".")[0]
    assert new_id != victim_id


def test_gemini_recipes_are_private_to_their_creator(client, other_visitor, fake_generator):
    fake_generator.recipes = [recipe(title="My Secret Skillet")]
    mine = client.post("/api/recipes/generate", json={"count": 1}).json()["created"][0]

    params = {"max_missing": 20}
    assert "My Secret Skillet" in {r["title"] for r in client.get("/api/recipes/matches", params=params).json()}
    assert "My Secret Skillet" not in {r["title"] for r in other_visitor.get("/api/recipes/matches", params=params).json()}
    assert other_visitor.get(f"/api/recipes/{mine['id']}").status_code == 404
    assert other_visitor.delete(f"/api/recipes/{mine['id']}").status_code == 404
    assert other_visitor.post("/api/meals", json={"recipe_id": mine["id"]}).status_code == 404


def test_two_visitors_can_each_get_a_recipe_with_the_same_title(client, other_visitor, fake_generator):
    fake_generator.recipes = [recipe(title="Sunny Bowl")]
    assert len(client.post("/api/recipes/generate", json={"count": 1}).json()["created"]) == 1
    assert len(other_visitor.post("/api/recipes/generate", json={"count": 1}).json()["created"]) == 1


def test_per_visitor_ai_limit(client, other_visitor, fake_generator, monkeypatch):
    monkeypatch.setattr(ai_limits, "AI_LIMIT_PER_VISITOR", 2)
    for _ in range(2):
        assert client.post("/api/recipes/generate", json={"count": 1}).status_code == 201
    res = client.post("/api/recipes/generate", json={"count": 1})
    assert res.status_code == 429 and "2 AI requests" in res.json()["detail"]
    # Photo scans share the same allowance...
    files = {"photo": ("f.png", PNG, "image/png")}
    assert client.post("/api/pantry/scan", files=files).status_code == 429
    # ...but other visitors are unaffected, and non-AI features keep working.
    assert other_visitor.post("/api/recipes/generate", json={"count": 1}).status_code == 201
    assert client.get("/api/recipes/matches").status_code == 200


def test_global_ai_limit(client, other_visitor, fake_generator, monkeypatch):
    monkeypatch.setattr(ai_limits, "AI_LIMIT_TOTAL", 1)
    assert client.post("/api/recipes/generate", json={"count": 1}).status_code == 201
    res = other_visitor.post("/api/recipes/generate", json={"count": 1})
    assert res.status_code == 429 and "today's AI allowance" in res.json()["detail"]


def test_failed_ai_calls_do_not_use_up_the_allowance(client, fake_generator, monkeypatch):
    from app.gemini import GeminiFailed

    monkeypatch.setattr(ai_limits, "AI_LIMIT_PER_VISITOR", 1)
    fake_generator.error = GeminiFailed("overloaded")
    assert client.post("/api/recipes/generate", json={"count": 1}).status_code == 502
    fake_generator.error = None
    assert client.post("/api/recipes/generate", json={"count": 1}).status_code == 201
