from app.gemini import GeminiFailed, GeminiUnavailable

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def test_add_list_and_remove(client, ids):
    eggs, spinach = ids("eggs", "spinach")
    res = client.post("/api/pantry", json={"ingredient_ids": [eggs, spinach], "source": "typed"})
    assert res.status_code == 201
    assert {item["name"] for item in res.json()} == {"eggs", "spinach"}

    assert client.delete(f"/api/pantry/{eggs}").status_code == 204
    assert [item["name"] for item in client.get("/api/pantry").json()] == ["spinach"]


def test_adding_twice_is_idempotent_and_keeps_original_source(client, ids):
    (eggs,) = ids("eggs")
    client.post("/api/pantry", json={"ingredient_ids": [eggs], "source": "photo"})
    items = client.post("/api/pantry", json={"ingredient_ids": [eggs], "source": "typed"}).json()
    assert len(items) == 1
    assert items[0]["source"] == "photo"


def test_unknown_ingredient_is_rejected_and_nothing_saved(client, ids):
    (eggs,) = ids("eggs")
    res = client.post("/api/pantry", json={"ingredient_ids": [eggs, 99999], "source": "typed"})
    assert res.status_code == 404
    assert client.get("/api/pantry").json() == []


def test_invalid_source_is_rejected(client, ids):
    res = client.post("/api/pantry", json={"ingredient_ids": ids("eggs"), "source": "magic"})
    assert res.status_code == 422


def test_removing_missing_item_returns_404(client, ids):
    assert client.delete(f"/api/pantry/{ids('eggs')[0]}").status_code == 404


def test_clear_pantry(client, ids):
    client.post("/api/pantry", json={"ingredient_ids": ids("eggs", "milk"), "source": "checklist"})
    assert client.delete("/api/pantry").status_code == 204
    assert client.get("/api/pantry").json() == []


def test_search_handles_prefix_alias_and_typo(client):
    def top(q):
        return client.get("/api/ingredients", params={"q": q}).json()[0]["name"]

    assert top("spin") == "spinach"
    assert top("garbanzo") == "chickpeas"     # alias
    assert top("courgette") == "zucchini"     # British alias
    assert top("brocoli") == "broccoli"       # typo -> trigram similarity


def test_search_hides_always_on_hand_basics(client):
    names = [i["name"] for i in client.get("/api/ingredients", params={"q": "salt"}).json()]
    assert "salt" not in names


def test_common_checklist(client):
    names = {i["name"] for i in client.get("/api/ingredients/common").json()}
    assert {"eggs", "olive oil", "spinach"} <= names
    assert "tempeh" not in names


def test_scan_maps_labels_to_catalog_without_saving(client, fake_detector):
    fake_detector.items = [
        ("Eggs", "high"),
        ("red bell peppers", "high"),
        ("baby spinach", "medium"),
        ("spinach", "high"),            # duplicate after mapping -> reported once
        ("kombucha", "low"),            # not in catalog -> unmatched
    ]
    res = client.post("/api/pantry/scan", files={"photo": ("fridge.png", PNG, "image/png")})
    assert res.status_code == 200
    body = res.json()
    assert [d["name"] for d in body["detected"]] == ["eggs", "bell pepper", "spinach"]
    assert body["detected"][2]["confidence"] == "medium"
    assert body["unmatched"] == ["kombucha"]
    assert client.get("/api/pantry").json() == []  # nothing saved until confirmed

    _, mime, vocabulary = fake_detector.calls[0]
    assert mime == "image/png"
    assert "chickpeas" in vocabulary and "salt" not in vocabulary


def test_scan_rejects_non_images(client, fake_detector):
    res = client.post("/api/pantry/scan", files={"photo": ("notes.txt", b"hi", "text/plain")})
    assert res.status_code == 415
    assert fake_detector.calls == []


def test_scan_without_api_key_returns_503(client, fake_detector):
    fake_detector.error = GeminiUnavailable("Set GEMINI_API_KEY")
    res = client.post("/api/pantry/scan", files={"photo": ("f.png", PNG, "image/png")})
    assert res.status_code == 503


def test_scan_model_failure_returns_502(client, fake_detector):
    fake_detector.error = GeminiFailed("boom")
    res = client.post("/api/pantry/scan", files={"photo": ("f.png", PNG, "image/png")})
    assert res.status_code == 502
