import { useEffect, useState } from "react";
import { api } from "../api.js";
import { TAG_LABELS, fmt } from "../nutrients.js";
import Modal from "./Modal.jsx";

export default function RecipeModal({ id, onClose, onLogged, onDeleted }) {
  const [recipe, setRecipe] = useState(null);
  const [servings, setServings] = useState(1);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.recipe(id).then(setRecipe).catch((e) => setError(e.message));
  }, [id]);

  const log = async () => {
    setSaving(true);
    try {
      await api.logMeal(id, servings);
      onLogged();
    } catch (e) {
      setError(e.message);
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!confirm(`Remove “${recipe.title}” from your menu?`)) return;
    try {
      await api.deleteRecipe(id);
      onDeleted(id);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Modal title={recipe?.title ?? "Recipe"} onClose={onClose}>
      {error && <p className="banner error">{error}</p>}
      {!recipe ? (
        <p className="muted">Loading…</p>
      ) : (
        <article className="recipe-detail">
          <span className="eyebrow">
            {recipe.meal_type} · {recipe.total_minutes} min · serves {recipe.servings}
            {recipe.source === "gemini" && <span className="ai-badge">✨ Created by Gemini</span>}
          </span>
          <h2>{recipe.title}</h2>
          <p className="muted">{recipe.description}</p>
          {recipe.conflicts.length > 0 && (
            <p className="banner error" role="alert">
              ⚠️ Contains {recipe.conflicts.join(", ")}, which is on your allergies / avoid list.
            </p>
          )}
          {recipe.tags.length > 0 && (
            <ul className="tags">
              {recipe.tags.map((t) => <li key={t} className={`tag tag-${t}`}>{TAG_LABELS[t]}</li>)}
            </ul>
          )}

          <dl className="macros big">
            <div><dt>Protein</dt><dd>{fmt(recipe.nutrition.protein_g)}g</dd></div>
            <div><dt>Veggies</dt><dd>{fmt(recipe.nutrition.veg_servings, 1)}</dd></div>
            <div><dt>Iron</dt><dd>{fmt(recipe.nutrition.iron_mg, 1)}mg</dd></div>
            <div><dt>Fiber</dt><dd>{fmt(recipe.nutrition.fiber_g)}g</dd></div>
            <div><dt>Energy</dt><dd>{fmt(recipe.nutrition.kcal)} kcal</dd></div>
          </dl>
          <p className="muted small">Per serving.</p>

          <div className="detail-cols">
            <section>
              <h3>Ingredients</h3>
              <ul className="ingredient-list">
                {recipe.ingredients.map((i) => (
                  <li key={i.ingredient_id} className={i.avoid ? "avoid" : i.have ? "have" : "need"}>
                    <span aria-hidden>{i.avoid ? "⚠" : i.have ? "✓" : "○"}</span>
                    <span>
                      {fmt(i.grams)} g {i.name}
                      {i.is_optional && <span className="muted small"> (optional)</span>}
                      {i.avoid && (
                        <span className="small avoid-note">
                          {i.is_optional ? " — skip it, you avoid this" : " — you avoid this"}
                        </span>
                      )}
                    </span>
                    {!i.have && !i.avoid && <span className="sr-only">(you need this)</span>}
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h3>Steps</h3>
              <ol className="steps">
                {recipe.steps.map((s, n) => <li key={n}>{s}</li>)}
              </ol>
            </section>
          </div>

          <div className="log-row">
            <label>
              Servings eaten
              <input
                type="number"
                min="0.25"
                max="10"
                step="0.25"
                value={servings}
                onChange={(e) => setServings(Number(e.target.value))}
              />
            </label>
            <div className="row gap">
              {recipe.source === "gemini" && (
                <button className="secondary" onClick={remove}>Remove recipe</button>
              )}
              <button className="primary" onClick={log} disabled={saving || !(servings > 0)}>
                {saving ? "Saving…" : "I ate this"}
              </button>
            </div>
          </div>
        </article>
      )}
    </Modal>
  );
}
