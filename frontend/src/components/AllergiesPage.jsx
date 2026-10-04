import { useEffect, useState } from "react";
import { api } from "../api.js";
import { ALLERGEN_LABELS } from "../nutrients.js";
import TypeAhead from "./TypeAhead.jsx";

// Every change saves immediately (PUT replaces the whole set). If a save fails,
// we fall back to what the server actually has, so the screen never lies
// about which allergies are active.
export default function AllergiesPage({ onChange }) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.allergies().then(setData).catch((e) => setStatus(e.message));
  }, []);

  const save = async (allergens, avoided) => {
    setData((d) => ({ ...d, allergens, avoided_ingredients: avoided }));
    setStatus("saving");
    try {
      const saved = await api.saveAllergies(allergens, avoided.map((i) => i.id));
      setData(saved);
      setStatus("saved");
      onChange?.(saved);
    } catch (e) {
      setStatus(e.message);
      api.allergies().then(setData).catch(() => {});
    }
  };

  if (!data) return <p className="muted">{status ?? "Loading…"}</p>;

  const selected = new Set(data.allergens);
  const avoidedIds = new Set(data.avoided_ingredients.map((i) => i.id));

  const toggleAllergen = (key) =>
    save(
      selected.has(key) ? data.allergens.filter((a) => a !== key) : [...data.allergens, key],
      data.avoided_ingredients,
    );

  const addFood = (_id, item) => save(data.allergens, [...data.avoided_ingredients, item]);
  const removeFood = (id) =>
    save(data.allergens, data.avoided_ingredients.filter((i) => i.id !== id));

  return (
    <div className="allergies-layout">
      <section className="card">
        <div className="row spread">
          <h2>Allergies</h2>
          <SaveStatus status={status} />
        </div>
        <p className="muted">
          Choose anything you're allergic to. Recipes containing it are hidden from your meal ideas
          and never added to your shopping list.
        </p>
        <div className="allergen-grid">
          {data.options.map((opt) => {
            const meta = ALLERGEN_LABELS[opt.key];
            const on = selected.has(opt.key);
            return (
              <label key={opt.key} className={on ? "allergen on" : "allergen"}>
                <input type="checkbox" checked={on} onChange={() => toggleAllergen(opt.key)} />
                <span className="allergen-icon" aria-hidden>{meta.icon}</span>
                <span>
                  <strong>{meta.label}</strong>
                  <span className="muted small allergen-examples">{opt.examples.join(", ")}</span>
                </span>
              </label>
            );
          })}
        </div>
      </section>

      <div className="stack">
        <section className="card">
          <h2>Other foods to avoid</h2>
          <p className="muted small">An intolerance, a sensitivity, or just a food you don't like.</p>
          <TypeAhead
            taken={avoidedIds}
            takenLabel="avoiding"
            onPick={addFood}
            placeholder="e.g. mushrooms, cilantro"
            autoFocus={false}
          />
          {data.avoided_ingredients.length > 0 && (
            <ul className="chips avoid-chips">
              {data.avoided_ingredients.map((i) => (
                <li key={i.id} className="chip avoid">
                  {i.name}
                  <button className="chip-x" aria-label={`Stop avoiding ${i.name}`} onClick={() => removeFood(i.id)}>
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card summary-card">
          <p>
            <strong>{data.hidden_recipe_count}</strong>{" "}
            {data.hidden_recipe_count === 1 ? "recipe is" : "recipes are"} hidden because of your choices.
          </p>
          <p className="muted small">
            Ingredients are flagged on the cautious side: soy sauce counts as gluten, oats count as
            gluten (they're often cross-contaminated), and dark chocolate counts as dairy and soy.
            Always check the labels on packaged foods, because brands differ.
          </p>
        </section>
      </div>
    </div>
  );
}

function SaveStatus({ status }) {
  if (!status) return null;
  if (status === "saving") return <span className="muted small" aria-live="polite">Saving…</span>;
  if (status === "saved") return <span className="ok small" aria-live="polite">Saved ✓</span>;
  return <span className="error-text small" role="alert">{status}</span>;
}
