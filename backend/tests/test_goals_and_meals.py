from datetime import date, timedelta

GOALS = {"kcal": 2200, "protein_g": 100, "veg_servings": 6, "fiber_g": 30, "iron_mg": 18}


def test_default_goals(client):
    assert client.get("/api/goals").json() == {
        "kcal": 2000, "protein_g": 90, "veg_servings": 5, "fiber_g": 28, "iron_mg": 18,
    }


def test_update_goals(client):
    assert client.put("/api/goals", json=GOALS).json() == GOALS
    assert client.get("/api/goals").json() == GOALS


def test_goal_validation(client):
    assert client.put("/api/goals", json={**GOALS, "protein_g": 5}).status_code == 422
    assert client.put("/api/goals", json={**GOALS, "kcal": 400}).status_code == 422


def test_log_meal_scales_by_servings_and_sums_the_day(client, recipe_id):
    rid = recipe_id("Red Lentil Soup")
    one = client.get(f"/api/recipes/{rid}").json()["nutrition"]

    logged = client.post("/api/meals", json={"recipe_id": rid, "servings": 2}).json()
    assert logged["title"] == "Red Lentil Soup"
    assert abs(logged["nutrition"]["protein_g"] - 2 * one["protein_g"]) < 0.01

    client.post("/api/meals", json={"recipe_id": rid, "servings": 0.5})
    day = client.get("/api/meals").json()
    assert len(day["meals"]) == 2
    assert abs(day["totals"]["iron_mg"] - 2.5 * one["iron_mg"]) < 0.01
    assert day["goals"]["protein_g"] == 90


def test_days_are_separate(client, recipe_id):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post("/api/meals", json={"recipe_id": recipe_id("Minestrone"), "eaten_on": yesterday})
    assert client.get("/api/meals").json()["meals"] == []
    assert len(client.get("/api/meals", params={"day": yesterday}).json()["meals"]) == 1


def test_empty_day_has_zero_totals(client):
    totals = client.get("/api/meals").json()["totals"]
    assert all(value == 0 for value in totals.values())


def test_delete_meal(client, recipe_id):
    meal = client.post("/api/meals", json={"recipe_id": recipe_id("Minestrone")}).json()
    assert client.delete(f"/api/meals/{meal['id']}").status_code == 204
    assert client.delete(f"/api/meals/{meal['id']}").status_code == 404


def test_meal_validation(client, recipe_id):
    assert client.post("/api/meals", json={"recipe_id": 99999}).status_code == 404
    rid = recipe_id("Minestrone")
    assert client.post("/api/meals", json={"recipe_id": rid, "servings": 0}).status_code == 422
    assert client.post("/api/meals", json={"recipe_id": rid, "servings": 11}).status_code == 422
