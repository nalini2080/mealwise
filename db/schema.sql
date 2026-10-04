-- MealWise schema
-- Nutrition is stored per 100 g on each ingredient; recipes list grams of each
-- ingredient, so every recipe's nutrition is derived (never duplicated) via views.

CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- fuzzy matching for search + photo labels

DROP VIEW IF EXISTS recipe_nutrition, profile_avoided CASCADE;
DROP TABLE IF EXISTS meal_logs, nutrition_goals, pantry_items, recipe_ingredients,
    recipes, profile_allergens, profile_avoided_ingredients, ingredient_allergens,
    ingredient_aliases, ingredients, ai_requests, profiles CASCADE;
DROP TYPE IF EXISTS pantry_source, meal_type, allergen, recipe_source, ai_kind CASCADE;

CREATE TYPE pantry_source AS ENUM ('photo', 'typed', 'checklist');
CREATE TYPE meal_type     AS ENUM ('breakfast', 'lunch', 'dinner', 'snack');
CREATE TYPE recipe_source AS ENUM ('curated', 'gemini');
CREATE TYPE ai_kind       AS ENUM ('scan', 'generate');
-- Based on the FDA's nine major food allergens. "gluten" stands in for the FDA's
-- "wheat" and is broader on purpose, so it also covers oats (usually
-- cross-contaminated) for people with celiac disease.
CREATE TYPE allergen      AS ENUM ('dairy', 'eggs', 'peanuts', 'tree_nuts', 'soy',
                                   'gluten', 'fish', 'shellfish', 'sesame');

-- One row per person. Visitors get an anonymous profile automatically (tracked
-- by a signed cookie); every per-person table hangs off profiles, so adding
-- real accounts later is a non-breaking change.
CREATE TABLE profiles (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ingredients (
    id               SERIAL PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    category         TEXT NOT NULL,
    -- nutrition per 100 g (USDA FoodData Central, rounded)
    kcal             NUMERIC(6,1) NOT NULL CHECK (kcal >= 0),
    protein_g        NUMERIC(5,1) NOT NULL CHECK (protein_g >= 0),
    carbs_g          NUMERIC(5,1) NOT NULL CHECK (carbs_g >= 0),
    fat_g            NUMERIC(5,1) NOT NULL CHECK (fat_g >= 0),
    fiber_g          NUMERIC(5,1) NOT NULL CHECK (fiber_g >= 0),
    iron_mg          NUMERIC(5,2) NOT NULL CHECK (iron_mg >= 0),
    is_vegetable     BOOLEAN NOT NULL DEFAULT false,  -- counts toward veggie servings
    is_healthy_fat   BOOLEAN NOT NULL DEFAULT false,  -- mostly unsaturated fat source
    is_common        BOOLEAN NOT NULL DEFAULT false,  -- shown on the quick-add checklist
    always_on_hand   BOOLEAN NOT NULL DEFAULT false   -- salt, pepper, water: never "missing"
);
CREATE INDEX ingredients_name_trgm ON ingredients USING gin (name gin_trgm_ops);

-- Alternate names ("garbanzo beans", "courgette") so search and photo labels
-- resolve to the canonical ingredient.
CREATE TABLE ingredient_aliases (
    alias          TEXT PRIMARY KEY,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE
);
CREATE INDEX ingredient_aliases_trgm ON ingredient_aliases USING gin (alias gin_trgm_ops);

-- Which allergens each ingredient contains (an ingredient can have several,
-- e.g. soy sauce = soy + gluten).
CREATE TABLE ingredient_allergens (
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    allergen       allergen NOT NULL,
    PRIMARY KEY (ingredient_id, allergen)
);
CREATE INDEX ingredient_allergens_allergen_idx ON ingredient_allergens (allergen);

CREATE TABLE recipes (
    id            SERIAL PRIMARY KEY,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    meal_type     meal_type NOT NULL,
    servings      INT NOT NULL CHECK (servings > 0),
    total_minutes INT NOT NULL CHECK (total_minutes > 0),
    steps         TEXT[] NOT NULL,
    source        recipe_source NOT NULL DEFAULT 'curated',
    -- Gemini recipes belong to the visitor who asked for them; curated ones to nobody.
    created_by    INT REFERENCES profiles(id) ON DELETE CASCADE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK ((source = 'curated') = (created_by IS NULL))
);
-- Titles are unique ignoring case within what one person can see (curated
-- recipes share owner 0), so Gemini can't add "chickpea curry" next to "Chickpea Curry".
CREATE UNIQUE INDEX recipes_title_owner_idx ON recipes (lower(title), COALESCE(created_by, 0));
CREATE INDEX recipes_created_by_idx ON recipes (created_by) WHERE created_by IS NOT NULL;

-- Many-to-many: which ingredients a recipe uses and how much.
CREATE TABLE recipe_ingredients (
    recipe_id      INT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    grams          NUMERIC(7,1) NOT NULL CHECK (grams > 0),
    is_optional    BOOLEAN NOT NULL DEFAULT false,  -- optional items never count as missing
    PRIMARY KEY (recipe_id, ingredient_id)
);
CREATE INDEX recipe_ingredients_ingredient_idx ON recipe_ingredients (ingredient_id);

CREATE TABLE pantry_items (
    profile_id     INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    source         pantry_source NOT NULL,
    added_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (profile_id, ingredient_id)
);

-- What a person must avoid: whole allergen groups, and/or specific foods
-- (an intolerance, or simply a dislike). Recipes using either are hidden.
CREATE TABLE profile_allergens (
    profile_id  INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    allergen    allergen NOT NULL,
    PRIMARY KEY (profile_id, allergen)
);

CREATE TABLE profile_avoided_ingredients (
    profile_id     INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    PRIMARY KEY (profile_id, ingredient_id)
);

-- Defaults are tuned for an active adult woman; every new profile starts here.
CREATE TABLE nutrition_goals (
    profile_id    INT PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    kcal          INT NOT NULL DEFAULT 2000 CHECK (kcal BETWEEN 1000 AND 5000),
    protein_g     INT NOT NULL DEFAULT 90   CHECK (protein_g BETWEEN 20 AND 300),
    veg_servings  INT NOT NULL DEFAULT 5    CHECK (veg_servings BETWEEN 1 AND 15),
    fiber_g       INT NOT NULL DEFAULT 28   CHECK (fiber_g BETWEEN 5 AND 80),
    iron_mg       INT NOT NULL DEFAULT 18   CHECK (iron_mg BETWEEN 5 AND 60),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE meal_logs (
    id          SERIAL PRIMARY KEY,
    profile_id  INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    recipe_id   INT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    servings    NUMERIC(4,2) NOT NULL CHECK (servings > 0 AND servings <= 10),
    eaten_on    DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX meal_logs_profile_day_idx ON meal_logs (profile_id, eaten_on);

-- One row per Gemini call, used to enforce daily limits (per visitor and
-- overall) so a public demo can't exhaust the free API quota.
CREATE TABLE ai_requests (
    id          BIGSERIAL PRIMARY KEY,
    profile_id  INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    kind        ai_kind NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ai_requests_created_idx ON ai_requests (created_at);
CREATE INDEX ai_requests_profile_idx ON ai_requests (profile_id, created_at);

-- Every ingredient a profile must avoid, from either source. Used by the
-- recipe matcher, recipe detail and shopping list so the rule lives in one place.
CREATE VIEW profile_avoided AS
SELECT pa.profile_id, ia.ingredient_id
FROM profile_allergens pa
JOIN ingredient_allergens ia ON ia.allergen = pa.allergen
UNION
SELECT profile_id, ingredient_id FROM profile_avoided_ingredients;

-- Per-serving nutrition for every recipe, derived from its ingredients.
-- One veggie serving = 80 g of vegetables (WHO / NHS "5 a day" portion).
CREATE VIEW recipe_nutrition AS
SELECT
    r.id AS recipe_id,
    ROUND(SUM(i.kcal      * ri.grams / 100) / r.servings, 0) AS kcal,
    ROUND(SUM(i.protein_g * ri.grams / 100) / r.servings, 1) AS protein_g,
    ROUND(SUM(i.carbs_g   * ri.grams / 100) / r.servings, 1) AS carbs_g,
    ROUND(SUM(i.fat_g     * ri.grams / 100) / r.servings, 1) AS fat_g,
    ROUND(SUM(i.fiber_g   * ri.grams / 100) / r.servings, 1) AS fiber_g,
    ROUND(SUM(i.iron_mg   * ri.grams / 100) / r.servings, 1) AS iron_mg,
    ROUND(COALESCE(SUM(ri.grams) FILTER (WHERE i.is_vegetable), 0) / 80.0 / r.servings, 1) AS veg_servings,
    BOOL_OR(i.is_healthy_fat AND ri.grams / r.servings >= 10) AS has_healthy_fat
FROM recipes r
JOIN recipe_ingredients ri ON ri.recipe_id = r.id
JOIN ingredients i         ON i.id = ri.ingredient_id
WHERE NOT ri.is_optional
GROUP BY r.id, r.servings;

-- Cycle-support tags. Thresholds are per serving:
--   iron-rich    >= 4.5 mg  (25% of the 18 mg daily value for menstruating women)
--   high-protein >= 25 g
--   high-fiber   >= 7 g     (25% of a 28 g day)
--   veggie-packed>= 2 servings
CREATE VIEW recipe_tags AS
SELECT
    recipe_id,
    ARRAY_REMOVE(ARRAY[
        CASE WHEN iron_mg      >= 4.5 THEN 'iron-rich'     END,
        CASE WHEN protein_g    >= 25  THEN 'high-protein'  END,
        CASE WHEN fiber_g      >= 7   THEN 'high-fiber'    END,
        CASE WHEN veg_servings >= 2 THEN 'veggie-packed' END,
        CASE WHEN has_healthy_fat     THEN 'healthy-fats'  END
    ], NULL) AS tags
FROM recipe_nutrition;
