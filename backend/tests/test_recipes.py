SCRAMBLE = "Spinach & Feta Scramble"


def add(client, ids, *names):
    client.post("/api/pantry", json={"ingredient_ids": ids(*names), "source": "typed"})


def by_title(matches):
    return {m["title"]: m for m in matches}


def test_full_pantry_recipe_ranks_first_with_nothing_missing(client, ids):
    add(client, ids, "eggs", "spinach", "feta", "olive oil")  # salt + pepper are always on hand
    matches = client.get("/api/recipes/matches", params={"max_missing": 0}).json()
    assert matches[0]["title"] == SCRAMBLE
    assert matches[0]["missing"] == []
    assert matches[0]["have_count"] == matches[0]["total_count"] == 6


def test_missing_ingredients_are_listed_and_filtered(client, ids):
    add(client, ids, "eggs", "spinach")
    scramble = by_title(client.get("/api/recipes/matches", params={"max_missing": 2}).json())[SCRAMBLE]
    assert scramble["missing"] == ["feta", "olive oil"]

    strict = client.get("/api/recipes/matches", params={"max_missing": 1}).json()
    assert SCRAMBLE not in by_title(strict)
    assert all(len(m["missing"]) <= 1 for m in strict)


def test_results_sorted_by_missing_count(client, ids):
    add(client, ids, "eggs", "spinach", "feta", "olive oil", "canned tomatoes", "onion")
    counts = [len(m["missing"]) for m in client.get("/api/recipes/matches").json()]
    assert counts == sorted(counts)


def test_optional_ingredients_never_count_as_missing(client, ids):
    add(client, ids, "eggs", "canned tomatoes", "bell pepper", "onion", "garlic",
        "cumin", "paprika", "olive oil", "feta", "parsley")
    shakshuka = by_title(client.get("/api/recipes/matches", params={"max_missing": 0}).json())["Shakshuka"]
    assert shakshuka["missing"] == []  # optional bread not required


def test_per_serving_nutrition_is_derived_from_ingredients(client, recipe_id):
    # 150 g eggs + 60 g spinach + 30 g feta + 5 g oil + 1 g salt + 1 g pepper, 1 serving
    recipe = client.get(f"/api/recipes/{recipe_id(SCRAMBLE)}").json()
    expected_protein = 150 * 0.126 + 60 * 0.029 + 30 * 0.142 + 1 * 0.104
    assert abs(recipe["nutrition"]["protein_g"] - expected_protein) < 0.1
    assert recipe["nutrition"]["veg_servings"] == round(60 / 80, 1)


def test_tags(client, recipe_id):
    lentil = client.get(f"/api/recipes/{recipe_id('Red Lentil Soup')}").json()
    assert {"iron-rich", "high-fiber", "veggie-packed"} <= set(lentil["tags"])

    only_iron = client.get("/api/recipes/matches", params={"tag": "iron-rich", "max_missing": 20}).json()
    assert only_iron and all("iron-rich" in m["tags"] for m in only_iron)


def test_meal_type_filter(client):
    res = client.get("/api/recipes/matches", params={"meal_type": "snack", "max_missing": 20}).json()
    assert res and {m["meal_type"] for m in res} == {"snack"}


def test_goal_score_favors_what_you_still_need(client, recipe_id):
    params = {"max_missing": 20, "sort": "goals"}
    fresh = by_title(client.get("/api/recipes/matches", params=params).json())

    # Eat a big veggie- and protein-heavy day; remaining gap shrinks so scores rise.
    for title in ("Turkey Bean Chili", "Sheet Pan Salmon & Sweet Potato", "Minestrone"):
        client.post("/api/meals", json={"recipe_id": recipe_id(title), "servings": 1})
    later = by_title(client.get("/api/recipes/matches", params=params).json())

    assert later["Tuna Lettuce Wraps"]["goal_score"] > fresh["Tuna Lettuce Wraps"]["goal_score"]
    assert all(0 <= m["goal_score"] <= 100 for m in later.values())


def test_sort_by_goals(client):
    scores = [m["goal_score"] for m in
              client.get("/api/recipes/matches", params={"sort": "goals", "max_missing": 20}).json()]
    assert scores == sorted(scores, reverse=True)


def test_recipe_detail_marks_what_you_have(client, ids, recipe_id):
    add(client, ids, "eggs")
    recipe = client.get(f"/api/recipes/{recipe_id(SCRAMBLE)}").json()
    have = {i["name"]: i["have"] for i in recipe["ingredients"]}
    assert have["eggs"] and have["salt"] and not have["feta"]
    assert len(recipe["steps"]) == 3


def test_unknown_recipe_404(client):
    assert client.get("/api/recipes/99999").status_code == 404


def test_shopping_list_combines_recipes_and_skips_what_you_have(client, ids, recipe_id):
    add(client, ids, "eggs")
    items = client.get("/api/shopping-list", params={
        "recipe_ids": [recipe_id(SCRAMBLE), recipe_id("Veggie Egg Muffins")]
    }).json()
    by_name = {i["name"]: i for i in items}
    assert "eggs" not in by_name and "salt" not in by_name
    assert by_name["spinach"]["grams"] == 120  # 60 g + 60 g
    assert len(by_name["spinach"]["for_recipes"]) == 2
