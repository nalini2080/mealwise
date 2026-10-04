import { useEffect, useState } from "react";
import { api } from "../api.js";
import { ALLERGEN_LABELS, GOALS, MEAL_TYPES, TAG_LABELS, fmt } from "../nutrients.js";
import RecipeModal from "./RecipeModal.jsx";
import ShoppingList from "./ShoppingList.jsx";

export default function MealsPage({ pantryCount, onLogged, onEditAllergies }) {
  const [filters, setFilters] = useState({ max_missing: 2, meal_type: "", tag: "", sort: "missing" });
  const [recipes, setRecipes] = useState(null);
  const [today, setToday] = useState(null);
  const [allergies, setAllergies] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [shopping, setShopping] = useState(new Set());
  const [showList, setShowList] = useState(false);
  const [error, setError] = useState(null);
  const [version, setVersion] = useState(0); // bump to refetch after generate/delete
  const [fresh, setFresh] = useState(null); // last Gemini batch: { created, rejected }
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api.matches(filters)
      .then((r) => !cancelled && setRecipes(r))
      .catch((e) => setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [filters, version]);

  const askGemini = async () => {
    setGenerating(true);
    setGenError(null);
    try {
      const result = await api.generateRecipes({
        count: 3, meal_type: filters.meal_type, focus: filters.tag,
      });
      setFresh(result);
      setVersion((v) => v + 1);
    } catch (e) {
      setGenError(e.message);
    } finally {
      setGenerating(false);
    }
  };

  const onDeleted = (id) => {
    setOpenId(null);
    setFresh((f) => f && { ...f, created: f.created.filter((r) => r.id !== id) });
    setShopping((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    setVersion((v) => v + 1);
  };

  useEffect(() => {
    api.today().then(setToday).catch(() => {});
    api.allergies().then(setAllergies).catch(() => {});
  }, []);

  const set = (key, value) => setFilters((f) => ({ ...f, [key]: value }));
  const toggleShopping = (id) =>
    setShopping((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  return (
    <div className="meals">
      {today && <RemainingStrip today={today} />}

      <section className="filters card" aria-label="Filters">
        <div className="field">
          <span className="field-label">Missing at most</span>
          <div className="segmented">
            {[0, 1, 2, 3].map((n) => (
              <button
                key={n}
                className={filters.max_missing === n ? "active" : undefined}
                onClick={() => set("max_missing", n)}
              >
                {n === 0 ? "Nothing" : n}
              </button>
            ))}
          </div>
        </div>
        <label className="field">
          <span className="field-label">Meal</span>
          <select value={filters.meal_type} onChange={(e) => set("meal_type", e.target.value)}>
            <option value="">Any</option>
            {MEAL_TYPES.map((m) => <option key={m} value={m}>{m[0].toUpperCase() + m.slice(1)}</option>)}
          </select>
        </label>
        <label className="field">
          <span className="field-label">Focus</span>
          <select value={filters.tag} onChange={(e) => set("tag", e.target.value)}>
            <option value="">Anything</option>
            {Object.entries(TAG_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </label>
        <label className="field">
          <span className="field-label">Sort by</span>
          <select value={filters.sort} onChange={(e) => set("sort", e.target.value)}>
            <option value="missing">Fewest missing ingredients</option>
            <option value="goals">Best for today's goals</option>
          </select>
        </label>
      </section>

      {allergies && <AvoidingNotice allergies={allergies} onEdit={onEditAllergies} />}

      <GeminiPanel
        generating={generating}
        error={genError}
        fresh={fresh}
        filters={filters}
        onAsk={askGemini}
        onDismiss={() => setFresh(null)}
        renderCard={(r) => (
          <RecipeCard
            key={r.id}
            recipe={r}
            onOpen={() => setOpenId(r.id)}
            inList={shopping.has(r.id)}
            onToggleList={() => toggleShopping(r.id)}
          />
        )}
      />
      {error && <p className="banner error">{error}</p>}
      {pantryCount === 0 && (
        <p className="banner">Your pantry is empty, so every ingredient counts as missing. Add what you have first.</p>
      )}

      {recipes === null ? (
        <p className="muted">Loading…</p>
      ) : recipes.length === 0 ? (
        <div className="empty card">
          <p>
            No recipes match yet. Try allowing more missing ingredients, add a few more to your
            pantry, or ask Gemini for new ideas built around what you have.
          </p>
        </div>
      ) : (
        <ul className="recipe-grid">
          {recipes.map((r) => (
            <RecipeCard
              key={r.id}
              recipe={r}
              onOpen={() => setOpenId(r.id)}
              inList={shopping.has(r.id)}
              onToggleList={() => toggleShopping(r.id)}
            />
          ))}
        </ul>
      )}

      {shopping.size > 0 && (
        <button className="primary floating" onClick={() => setShowList(true)}>
          🛒 Shopping list ({shopping.size} {shopping.size === 1 ? "recipe" : "recipes"})
        </button>
      )}

      {openId && (
        <RecipeModal
          id={openId}
          onClose={() => setOpenId(null)}
          onDeleted={onDeleted}
          onLogged={() => {
            setOpenId(null);
            onLogged();
          }}
        />
      )}
      {showList && (
        <ShoppingList
          recipeIds={[...shopping]}
          onClose={() => setShowList(false)}
          onClear={() => {
            setShopping(new Set());
            setShowList(false);
          }}
        />
      )}
    </div>
  );
}

function GeminiPanel({ generating, error, fresh, filters, onAsk, onDismiss, renderCard }) {
  const scope = [
    filters.meal_type,
    filters.tag && TAG_LABELS[filters.tag].toLowerCase(),
  ].filter(Boolean).join(", ");
  return (
    <section className="gemini card" aria-live="polite">
      <div className="gemini-row">
        <div>
          <h2>✨ Want something new?</h2>
          <p className="muted small">
            Gemini writes recipes around your pantry, what you still need today and your allergies
            {scope && <> (matching your filters: <strong>{scope}</strong>)</>}. They're added to
            your menu for good.
          </p>
        </div>
        <button className="primary gemini-btn" onClick={onAsk} disabled={generating}>
          {generating ? <><span className="spinner" aria-hidden /> Writing recipes…</> : "Ask Gemini for 3 ideas"}
        </button>
      </div>
      {generating && (
        <p className="muted small">This usually takes about 30 seconds. Every recipe is checked against your allergies before it's saved.</p>
      )}
      {error && <p className="banner error" role="alert">{error}</p>}
      {fresh && (
        <div className="fresh">
          <div className="row spread">
            <h3>
              {fresh.created.length > 0
                ? `Fresh from Gemini: ${fresh.created.length} new recipe${fresh.created.length === 1 ? "" : "s"}`
                : "No new recipes this time"}
            </h3>
            <button className="link" onClick={onDismiss}>Hide</button>
          </div>
          {fresh.created.length > 0 && <ul className="recipe-grid">{fresh.created.map(renderCard)}</ul>}
          {fresh.rejected.length > 0 && (
            <details className="small muted rejected">
              <summary>
                {fresh.rejected.length} idea{fresh.rejected.length === 1 ? " was" : "s were"} skipped by our safety checks
              </summary>
              <ul>
                {fresh.rejected.map((r, n) => <li key={n}><strong>{r.title}</strong>: {r.reason}</li>)}
              </ul>
            </details>
          )}
        </div>
      )}
    </section>
  );
}

function AvoidingNotice({ allergies, onEdit }) {
  const names = [
    ...allergies.allergens.map((a) => ALLERGEN_LABELS[a].label.toLowerCase()),
    ...allergies.avoided_ingredients.map((i) => i.name),
  ];
  if (names.length === 0) {
    return (
      <p className="muted small avoiding">
        Have food allergies? <button className="link" onClick={onEdit}>Add them</button> and we'll
        hide recipes that contain them.
      </p>
    );
  }
  return (
    <p className="banner avoiding">
      <span>
        🛡️ Avoiding <strong>{names.join(", ")}</strong>
        {allergies.hidden_recipe_count > 0 &&
          ` · ${allergies.hidden_recipe_count} recipe${allergies.hidden_recipe_count === 1 ? "" : "s"} hidden`}
      </span>
      <button className="link" onClick={onEdit}>Edit</button>
    </p>
  );
}

function RemainingStrip({ today }) {
  const left = GOALS.filter((g) => g.key !== "kcal").map((g) => ({
    ...g,
    value: Math.max(today.goals[g.key] - today.totals[g.key], 0),
  }));
  return (
    <div className="remaining" aria-label="Still to go today">
      <span className="remaining-title">Still to go today</span>
      {left.map((g) => (
        <span key={g.key} className="remaining-item">
          <strong>{fmt(g.value, 1)}</strong> {g.unit === "servings" ? "veggie servings" : `${g.unit} ${g.label.toLowerCase()}`}
        </span>
      ))}
    </div>
  );
}

function RecipeCard({ recipe: r, onOpen, inList, onToggleList }) {
  const pct = Math.round((100 * r.have_count) / r.total_count);
  return (
    <li className="recipe-card card">
      <button className="recipe-open" onClick={onOpen} aria-label={`Open ${r.title}`}>
        <div className="row spread">
          <span className="eyebrow">
            {r.meal_type} · {r.total_minutes} min
            {r.source === "gemini" && <span className="ai-badge">✨ Gemini</span>}
          </span>
          <span className="score" title="How much of what you still need today (protein, veggies, iron, fiber) one serving covers">
            {r.goal_score}%<small>of today's needs</small>
          </span>
        </div>
        <h3>{r.title}</h3>
        <p className="muted small">{r.description}</p>

        <div className="have-bar" aria-label={`You have ${r.have_count} of ${r.total_count} ingredients`}>
          <div style={{ width: `${pct}%` }} />
        </div>
        <p className="small">
          {r.missing.length === 0 ? (
            <strong className="ok">You have everything ✓</strong>
          ) : (
            <>Need: <span className="missing">{r.missing.join(", ")}</span></>
          )}
        </p>

        <dl className="macros">
          <div><dt>Protein</dt><dd>{fmt(r.nutrition.protein_g)}g</dd></div>
          <div><dt>Veg</dt><dd>{fmt(r.nutrition.veg_servings, 1)}</dd></div>
          <div><dt>Iron</dt><dd>{fmt(r.nutrition.iron_mg, 1)}mg</dd></div>
          <div><dt>Fiber</dt><dd>{fmt(r.nutrition.fiber_g)}g</dd></div>
          <div><dt>kcal</dt><dd>{fmt(r.nutrition.kcal)}</dd></div>
        </dl>
        {r.tags.length > 0 && (
          <ul className="tags">
            {r.tags.map((t) => <li key={t} className={`tag tag-${t}`}>{TAG_LABELS[t]}</li>)}
          </ul>
        )}
      </button>
      {r.missing.length > 0 && (
        <label className="add-to-list small">
          <input type="checkbox" checked={inList} onChange={onToggleList} /> Add missing items to shopping list
        </label>
      )}
    </li>
  );
}
