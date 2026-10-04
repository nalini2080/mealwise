from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

PantrySource = Literal["photo", "typed", "checklist"]
MealType = Literal["breakfast", "lunch", "dinner", "snack"]
Confidence = Literal["high", "medium", "low"]
RecipeSource = Literal["curated", "gemini"]
Tag = Literal["iron-rich", "high-protein", "high-fiber", "veggie-packed", "healthy-fats"]
Allergen = Literal[
    "dairy", "eggs", "peanuts", "tree_nuts", "soy", "gluten", "fish", "shellfish", "sesame"
]


class Ingredient(BaseModel):
    id: int
    name: str
    category: str


class PantryItem(BaseModel):
    ingredient_id: int
    name: str
    category: str
    source: PantrySource
    added_at: datetime


class PantryAdd(BaseModel):
    ingredient_ids: list[int] = Field(min_length=1, max_length=200)
    source: PantrySource


class DetectedIngredient(BaseModel):
    label: str  # what the model saw, e.g. "red bell peppers"
    ingredient_id: int
    name: str  # the catalog ingredient it resolved to
    confidence: Confidence


class ScanResult(BaseModel):
    detected: list[DetectedIngredient]
    unmatched: list[str]  # labels we could not map to a known ingredient


class Nutrition(BaseModel):
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    iron_mg: float
    veg_servings: float


class RecipeMatch(BaseModel):
    id: int
    title: str
    description: str
    meal_type: MealType
    servings: int
    total_minutes: int
    source: RecipeSource
    tags: list[str]
    nutrition: Nutrition  # per serving
    missing: list[str]
    conflicts: list[str]  # required ingredients you avoid; only non-empty on recipe detail
    have_count: int
    total_count: int
    goal_score: int  # 0-100: how much of today's remaining gap one serving closes


class RecipeIngredient(BaseModel):
    ingredient_id: int
    name: str
    grams: float
    is_optional: bool
    have: bool
    avoid: bool  # matches one of your allergies or avoided foods


class RecipeDetail(RecipeMatch):
    steps: list[str]
    ingredients: list[RecipeIngredient]


class ShoppingItem(BaseModel):
    ingredient_id: int
    name: str
    category: str
    grams: float
    for_recipes: list[str]


class Goals(BaseModel):
    kcal: int = Field(ge=1000, le=5000)
    protein_g: int = Field(ge=20, le=300)
    veg_servings: int = Field(ge=1, le=15)
    fiber_g: int = Field(ge=5, le=80)
    iron_mg: int = Field(ge=5, le=60)


class MealLogIn(BaseModel):
    recipe_id: int
    servings: float = Field(default=1, gt=0, le=10)
    eaten_on: date | None = None


class MealLog(BaseModel):
    id: int
    recipe_id: int
    title: str
    meal_type: MealType
    servings: float
    nutrition: Nutrition  # already multiplied by servings


class DaySummary(BaseModel):
    day: date
    goals: Goals
    totals: Nutrition
    meals: list[MealLog]


class AllergenOption(BaseModel):
    key: Allergen
    examples: list[str]


class Allergies(BaseModel):
    allergens: list[Allergen]
    avoided_ingredients: list[Ingredient]
    options: list[AllergenOption]
    hidden_recipe_count: int


class AllergiesUpdate(BaseModel):
    allergens: list[Allergen] = Field(default_factory=list, max_length=9)
    avoided_ingredient_ids: list[int] = Field(default_factory=list, max_length=100)


class GenerateRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=5)
    meal_type: MealType | None = None
    focus: Tag | None = None


class RejectedRecipe(BaseModel):
    title: str
    reason: str


class GenerateResult(BaseModel):
    created: list[RecipeMatch]
    rejected: list[RejectedRecipe]
