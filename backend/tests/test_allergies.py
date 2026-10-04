def set_allergies(client, allergens=(), avoided_ids=()):
    res = client.put("/api/allergies", json={
        "allergens": list(allergens), "avoided_ingredient_ids": list(avoided_ids),
    })
    assert res.status_code == 200, res.text
    return res.json()


def all_matches(client, **params):
    return client.get("/api/recipes/matches", params={"max_missing": 20, **params}).json()


def recipe_ingredients(client, recipe_id):
    return {i["name"] for i in client.get(f"/api/recipes/{recipe_id}").json()["ingredients"]
            if not i["is_optional"]}


def test_starts_empty_and_lists_all_nine_allergens_with_examples(client):
    body = client.get("/api/allergies").json()
    assert body["allergens"] == [] and body["avoided_ingredients"] == []
    assert body["hidden_recipe_count"] == 0
    options = {o["key"]: o["examples"] for o in body["options"]}
    assert set(options) == {"dairy", "eggs", "peanuts", "tree_nuts", "soy",
                            "gluten", "fish", "shellfish", "sesame"}
    assert "feta" in options["dairy"] and "soy sauce" in options["gluten"]


def test_allergen_hides_every_recipe_containing_it(client, ids):
    (peanut_butter,) = ids("peanut butter")
    before = all_matches(client)
    body = set_allergies(client, allergens=["peanuts"])
    after = all_matches(client)

    hidden = {r["title"] for r in before} - {r["title"] for r in after}
    assert {"Apple & Peanut Butter", "Peanut Tofu Noodles", "Green Protein Smoothie"} <= hidden
    assert body["hidden_recipe_count"] == len(hidden)
    for r in after:  # nothing left uses peanut butter
        assert "peanut butter" not in recipe_ingredients(client, r["id"])


def test_ingredient_with_two_allergens_is_caught_by_either(client):
    set_allergies(client, allergens=["gluten"])
    titles = {r["title"] for r in all_matches(client)}
    assert "Beef & Broccoli" not in titles      # soy sauce contains wheat
    assert "Berry Chia Overnight Oats" not in titles  # oats: cross-contact risk
    assert "Sheet Pan Salmon & Sweet Potato" in titles


def test_avoiding_a_specific_food(client, ids):
    (mushrooms,) = ids("mushrooms")
    body = set_allergies(client, avoided_ids=[mushrooms])
    assert [i["name"] for i in body["avoided_ingredients"]] == ["mushrooms"]
    titles = {r["title"] for r in all_matches(client)}
    assert "Ginger Tofu & Bok Choy" not in titles
    assert "Mushroom Spinach Quesadillas" not in titles


def test_allergens_and_foods_combine(client, ids):
    body = set_allergies(client, allergens=["fish", "shellfish"], avoided_ids=ids("kale"))
    titles = {r["title"] for r in all_matches(client)}
    for gone in ("Sheet Pan Salmon & Sweet Potato", "Shrimp Veggie Stir-Fry", "Chicken Kale Caesar"):
        assert gone not in titles
    assert body["allergens"] == ["fish", "shellfish"]


def test_optional_allergen_does_not_hide_recipe_but_is_flagged(client, recipe_id):
    set_allergies(client, allergens=["gluten"])  # Shakshuka's bread is optional
    assert "Shakshuka" in {r["title"] for r in all_matches(client)}
    detail = client.get(f"/api/recipes/{recipe_id('Shakshuka')}").json()
    bread = next(i for i in detail["ingredients"] if i["name"] == "whole wheat bread")
    assert bread["avoid"] and bread["is_optional"]
    assert detail["conflicts"] == []


def test_detail_of_hidden_recipe_explains_conflict(client, recipe_id):
    set_allergies(client, allergens=["dairy"])
    detail = client.get(f"/api/recipes/{recipe_id('Spinach & Feta Scramble')}").json()
    assert detail["conflicts"] == ["feta"]
    assert {i["name"] for i in detail["ingredients"] if i["avoid"]} == {"feta"}


def test_shopping_list_never_suggests_avoided_food(client, recipe_id):
    set_allergies(client, allergens=["dairy"])
    items = client.get("/api/shopping-list", params={
        "recipe_ids": [recipe_id("Spinach & Feta Scramble")]}).json()
    names = {i["name"] for i in items}
    assert "feta" not in names and "eggs" in names


def test_put_replaces_the_whole_set(client, ids):
    set_allergies(client, allergens=["eggs", "soy"], avoided_ids=ids("kale"))
    body = set_allergies(client, allergens=["sesame"])
    assert body["allergens"] == ["sesame"]
    assert body["avoided_ingredients"] == []


def test_clearing_allergies_restores_recipes(client):
    everything = len(all_matches(client))
    set_allergies(client, allergens=["dairy", "gluten"])
    assert len(all_matches(client)) < everything
    set_allergies(client)
    assert len(all_matches(client)) == everything


def test_validation(client):
    assert client.put("/api/allergies", json={"allergens": ["chocolate"]}).status_code == 422
    res = client.put("/api/allergies", json={"avoided_ingredient_ids": [99999]})
    assert res.status_code == 404
    assert client.get("/api/allergies").json()["allergens"] == []  # nothing half-saved


def test_duplicates_are_ignored(client, ids):
    body = set_allergies(client, allergens=["eggs", "eggs"], avoided_ids=ids("kale") * 2)
    assert body["allergens"] == ["eggs"]
    assert len(body["avoided_ingredients"]) == 1
