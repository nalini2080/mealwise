"""Ask Gemini to invent new recipes from the user's pantry, goals and allergies.

Gemini only proposes *ingredients and grams*. It never supplies nutrition:
every number the app shows is still calculated by the database from the
ingredient catalog, so generated recipes are exactly as trustworthy as the
curated ones. Everything Gemini returns is validated before saving
(see routers/generate.py).
"""

from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel

from app.gemini import GeminiClient, gemini
from app.schemas import MealType


class GeneratedIngredient(BaseModel):
    name: str
    grams: float
    optional: bool


class GeneratedRecipe(BaseModel):
    title: str
    description: str
    meal_type: MealType
    servings: int
    total_minutes: int
    steps: list[str]
    ingredients: list[GeneratedIngredient]


@dataclass
class RecipeRequest:
    count: int
    allowed: list[str]          # catalog names minus anything the user avoids
    pantry: list[str]           # what the user has right now
    avoid: list[str]            # allergens/foods, named explicitly as a hard rule
    remaining: dict[str, float]  # today's remaining protein_g / veg_servings / iron_mg / fiber_g
    existing_titles: list[str]
    meal_type: str | None = None
    focus: str | None = None    # one of the recipe tags, e.g. "iron-rich"


class RecipeGenerator(Protocol):
    def generate(self, request: RecipeRequest) -> list[GeneratedRecipe]: ...


PROMPT = """You are a recipe developer for MealWise, an app that suggests home-cooked
meals from what someone already has and what their body needs today.

Create {count} new, realistic, distinct recipes{meal_clause}.

HARD RULES (recipes that break these are thrown away):
1. Use ONLY ingredients from the ALLOWED list, spelled exactly as written there.
2. NEVER use any of these (allergies / foods the user avoids): {avoid}.
3. Do not repeat or lightly rename any EXISTING recipe.
4. "grams" is the total for the whole recipe (all servings combined), in realistic amounts.
5. 3 to 6 short, clear steps. servings between 1 and 6. total_minutes realistic.
6. Mark garnishes and serve-with sides as optional: true; everything else optional: false.

PREFERENCES:
- Build mostly from the PANTRY so the user is missing as few ingredients as possible.
- Help close what they still need today: {protein} g protein, {veg} veggie servings
  (1 serving = 80 g of vegetables), {iron} mg iron, {fiber} g fiber. One serving of a
  main meal should cover roughly a third of that; snacks less.
  Pair plant iron with vitamin C (peppers, tomatoes, citrus) where it fits.
{focus_clause}- Vary cuisines and cooking methods; no two recipes should feel alike.
- Titles: short and appetizing, under 50 characters.

ALLOWED: {allowed}

PANTRY: {pantry}

EXISTING: {existing}"""

FOCUS_TEXT = {
    "iron-rich": "rich in iron (at least 4.5 mg per serving)",
    "high-protein": "high in protein (at least 25 g per serving)",
    "high-fiber": "high in fiber (at least 7 g per serving)",
    "veggie-packed": "packed with vegetables (at least 2 servings per portion)",
    "healthy-fats": "built around healthy fats (olive oil, nuts, seeds, avocado or oily fish)",
}


def build_prompt(req: RecipeRequest) -> str:
    focus = FOCUS_TEXT.get(req.focus or "")
    return PROMPT.format(
        count=req.count,
        meal_clause=f" for {req.meal_type}" if req.meal_type else " across breakfast, lunch, dinner or snacks",
        avoid=", ".join(req.avoid) or "nothing",
        protein=round(req.remaining["protein_g"]),
        veg=round(req.remaining["veg_servings"], 1),
        iron=round(req.remaining["iron_mg"], 1),
        fiber=round(req.remaining["fiber_g"]),
        focus_clause=f"- Every recipe must be {focus}.\n" if focus else "",
        allowed=", ".join(req.allowed),
        pantry=", ".join(req.pantry) or "(empty: use common staples from ALLOWED)",
        existing="; ".join(req.existing_titles),
    )


class GeminiRecipeGenerator:
    def __init__(self, client: GeminiClient = gemini):
        self.client = client

    def generate(self, request: RecipeRequest) -> list[GeneratedRecipe]:
        return self.client.generate_json(
            contents=[build_prompt(request)],
            schema=list[GeneratedRecipe],
            temperature=0.9,  # we want variety here
        )


_generator: RecipeGenerator = GeminiRecipeGenerator()


def get_recipe_generator() -> RecipeGenerator:
    """FastAPI dependency; overridden with a fake in tests."""
    return _generator
