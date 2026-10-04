// Thin wrapper over the FastAPI backend. Every call throws an Error whose
// message is the API's `detail`, so components can show it directly.

async function request(path, { method = "GET", body, form } = {}) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: form ?? (body ? JSON.stringify(body) : undefined),
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join("; ")
      : detail || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

const qs = (params) => {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    for (const v of [].concat(value)) search.append(key, v);
  }
  return search.toString();
};

export const api = {
  searchIngredients: (q) => request(`/ingredients?${qs({ q })}`),
  commonIngredients: () => request("/ingredients/common"),

  pantry: () => request("/pantry"),
  addToPantry: (ingredientIds, source) =>
    request("/pantry", { method: "POST", body: { ingredient_ids: ingredientIds, source } }),
  removeFromPantry: (id) => request(`/pantry/${id}`, { method: "DELETE" }),
  clearPantry: () => request("/pantry", { method: "DELETE" }),
  scanPhoto: (file) => {
    const form = new FormData();
    form.append("photo", file);
    return request("/pantry/scan", { method: "POST", form });
  },

  matches: (filters) => request(`/recipes/matches?${qs(filters)}`),
  recipe: (id) => request(`/recipes/${id}`),
  generateRecipes: ({ count = 3, meal_type, focus } = {}) =>
    request("/recipes/generate", {
      method: "POST",
      body: { count, meal_type: meal_type || null, focus: focus || null },
    }),
  deleteRecipe: (id) => request(`/recipes/${id}`, { method: "DELETE" }),
  shoppingList: (recipeIds) => request(`/shopping-list?${qs({ recipe_ids: recipeIds })}`),

  goals: () => request("/goals"),
  saveGoals: (goals) => request("/goals", { method: "PUT", body: goals }),

  allergies: () => request("/allergies"),
  saveAllergies: (allergens, avoidedIngredientIds) =>
    request("/allergies", {
      method: "PUT",
      body: { allergens, avoided_ingredient_ids: avoidedIngredientIds },
    }),

  today: () => request("/meals"),
  logMeal: (recipeId, servings) =>
    request("/meals", { method: "POST", body: { recipe_id: recipeId, servings } }),
  deleteMeal: (id) => request(`/meals/${id}`, { method: "DELETE" }),
};
