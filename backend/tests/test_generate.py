from app.gemini import GeminiFailed, GeminiUnavailable
from app.recipe_ai import GeneratedIngredient, GeneratedRecipe, RecipeRequest, build_prompt


def recipe(title="Lemony Chickpea Spinach Skillet", ingredients=None, **overrides):
    ingredients = ingredients or [
        ("chickpeas", 240, False), ("spinach", 150, False), ("canned tomatoes", 400, False),
        ("olive oil", 15, False), ("lemon", 20, False), ("salt", 2, False),
    ]
    fields = dict(
        title=title, description="Quick, iron-rich and bright.", meal_type="dinner",
        servings=2, total_minutes=20, steps=["Warm the oil.", "Simmer everything.", "Finish with lemon."],
        ingredients=[GeneratedIngredient(name=n, grams=g, optional=o) for n, g, o in ingredients],
    )
    return GeneratedRecipe(**{**fields, **overrides})


def generate(client, **body):
    return client.post("/api/recipes/generate", json=body)


def test_valid_recipe_is_saved_with_nutrition_computed_by_the_database(client, fake_generator):
    fake_generator.recipes = [recipe()]
    res = generate(client, count=1)
    assert res.status_code == 201
    body = res.json()
    assert body["rejected"] == []
    (new,) = body["created"]
    assert new["source"] == "gemini"
    # 240 g chickpeas (2.9 mg/100 g) + 150 g spinach (2.7) + 400 g tomatoes (1.1) + ... over 2 servings
    assert new["nutrition"]["iron_mg"] > 6
    assert "iron-rich" in new["tags"]

    # It's now a normal part of the menu.
    titles = {r["title"] for r in client.get("/api/recipes/matches", params={"max_missing": 20}).json()}
    assert "Lemony Chickpea Spinach Skillet" in titles


def test_prompt_context_uses_pantry_goals_and_allergies(client, fake_generator, ids):
    client.post("/api/pantry", json={"ingredient_ids": ids("eggs", "spinach"), "source": "typed"})
    client.put("/api/allergies", json={"allergens": ["peanuts"], "avoided_ingredient_ids": ids("kale")})
    generate(client, count=2, meal_type="breakfast", focus="high-protein")

    req = fake_generator.requests[0]
    assert req.count == 2 and req.meal_type == "breakfast" and req.focus == "high-protein"
    assert req.pantry == ["eggs", "spinach"]
    assert set(req.avoid) == {"peanut butter", "kale"}
    assert "peanut butter" not in req.allowed and "kale" not in req.allowed
    assert req.remaining["protein_g"] == 90
    assert "Shakshuka" in req.existing_titles


def test_unknown_ingredient_is_rejected(client, fake_generator):
    fake_generator.recipes = [recipe(ingredients=[("chickpeas", 200, False), ("dragon fruit", 100, False)])]
    body = generate(client, count=1).json()
    assert body["created"] == []
    assert "dragon fruit" in body["rejected"][0]["reason"]


def test_allergen_is_rejected_even_if_the_model_ignores_the_prompt(client, fake_generator):
    client.put("/api/allergies", json={"allergens": ["dairy"]})
    fake_generator.recipes = [recipe(ingredients=[("chickpeas", 200, False), ("feta", 60, False)])]
    body = generate(client, count=1).json()
    assert body["created"] == []
    assert "feta" in body["rejected"][0]["reason"]


def test_alias_resolving_to_an_avoided_food_is_still_caught(client, fake_generator):
    client.put("/api/allergies", json={"allergens": ["dairy"]})
    fake_generator.recipes = [recipe(ingredients=[("chickpeas", 200, False), ("yoghurt", 100, False)])]
    assert generate(client, count=1).json()["created"] == []


def test_aliases_and_case_are_resolved(client, fake_generator):
    fake_generator.recipes = [recipe(ingredients=[("Garbanzo Beans", 240, False), ("baby spinach", 100, False)])]
    body = generate(client, count=1).json()
    assert len(body["created"]) == 1


def test_duplicate_titles_are_rejected_case_insensitively(client, fake_generator):
    fake_generator.recipes = [recipe(title="shakshuka"), recipe(title="Brand New Bowl"),
                              recipe(title="BRAND NEW BOWL")]
    body = generate(client, count=3).json()
    assert [r["title"] for r in body["created"]] == ["Brand New Bowl"]
    assert len(body["rejected"]) == 2


def test_duplicate_ingredients_are_merged(client, fake_generator, recipe_id):
    fake_generator.recipes = [recipe(ingredients=[
        ("chickpeas", 100, False), ("chickpeas", 140, False), ("spinach", 80, False)])]
    new = generate(client, count=1).json()["created"][0]
    detail = client.get(f"/api/recipes/{new['id']}").json()
    assert {i["name"]: i["grams"] for i in detail["ingredients"]}["chickpeas"] == 240


def test_unrealistic_recipes_are_rejected(client, fake_generator):
    fake_generator.recipes = [
        recipe(title="Huge", ingredients=[("chickpeas", 99999, False), ("spinach", 50, False)]),
        recipe(title="Just Salt", ingredients=[("salt", 5, False), ("water", 500, False)]),
        recipe(title="No Steps", steps=["  "]),
        recipe(title="Forever Stew", total_minutes=9000),
    ]
    body = generate(client, count=4).json()
    assert body["created"] == [] and len(body["rejected"]) == 4


def test_extra_recipes_beyond_count_are_ignored(client, fake_generator):
    fake_generator.recipes = [recipe(title=f"Bowl {n}") for n in range(4)]
    assert len(generate(client, count=2).json()["created"]) == 2


def test_errors_map_to_status_codes(client, fake_generator):
    fake_generator.error = GeminiUnavailable("no key")
    assert generate(client).status_code == 503
    fake_generator.error = GeminiFailed("busy")
    assert generate(client).status_code == 502


def test_request_validation(client, fake_generator):
    assert generate(client, count=0).status_code == 422
    assert generate(client, count=6).status_code == 422
    assert generate(client, focus="spicy").status_code == 422


def test_delete_rules(client, fake_generator, recipe_id):
    fake_generator.recipes = [recipe(title="Keep Me"), recipe(title="Toss Me")]
    keep, toss = generate(client, count=2).json()["created"]

    assert client.delete(f"/api/recipes/{recipe_id('Shakshuka')}").status_code == 403
    client.post("/api/meals", json={"recipe_id": keep["id"]})
    assert client.delete(f"/api/recipes/{keep['id']}").status_code == 409
    assert client.delete(f"/api/recipes/{toss['id']}").status_code == 204
    assert client.get(f"/api/recipes/{toss['id']}").status_code == 404
    assert client.delete("/api/recipes/99999").status_code == 404


def test_prompt_states_the_hard_rules():
    prompt = build_prompt(RecipeRequest(
        count=3, allowed=["eggs", "spinach"], pantry=["eggs"], avoid=["peanut butter"],
        remaining={"protein_g": 60, "veg_servings": 3, "iron_mg": 10, "fiber_g": 20},
        existing_titles=["Shakshuka"], meal_type="lunch", focus="iron-rich",
    ))
    assert "NEVER use any of these" in prompt and "peanut butter" in prompt
    assert "ALLOWED: eggs, spinach" in prompt
    assert "for lunch" in prompt and "rich in iron" in prompt
