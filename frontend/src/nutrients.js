// Display metadata for the five tracked goals, in display order.
export const GOALS = [
  { key: "protein_g", label: "Protein", unit: "g", step: 5 },
  { key: "veg_servings", label: "Veggies", unit: "servings", step: 1 },
  { key: "iron_mg", label: "Iron", unit: "mg", step: 1 },
  { key: "fiber_g", label: "Fiber", unit: "g", step: 1 },
  { key: "kcal", label: "Energy", unit: "kcal", step: 50 },
];

export const TAG_LABELS = {
  "iron-rich": "Iron-rich",
  "high-protein": "High protein",
  "high-fiber": "High fiber",
  "veggie-packed": "Veggie-packed",
  "healthy-fats": "Healthy fats",
};

export const MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"];

export const fmt = (value, digits = 0) =>
  Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });

export const ALLERGEN_LABELS = {
  dairy: { label: "Dairy", icon: "🥛" },
  eggs: { label: "Eggs", icon: "🥚" },
  peanuts: { label: "Peanuts", icon: "🥜" },
  tree_nuts: { label: "Tree nuts", icon: "🌰" },
  soy: { label: "Soy", icon: "🫘" },
  gluten: { label: "Gluten / wheat", icon: "🌾" },
  fish: { label: "Fish", icon: "🐟" },
  shellfish: { label: "Shellfish", icon: "🦐" },
  sesame: { label: "Sesame", icon: "⚪" },
};
