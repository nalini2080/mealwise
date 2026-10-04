import { useState } from "react";
import { api } from "../api.js";
import PhotoScan from "./PhotoScan.jsx";
import TypeAhead from "./TypeAhead.jsx";
import Checklist from "./Checklist.jsx";

const METHODS = [
  { id: "photo", icon: "📷", label: "Snap a photo", hint: "We'll spot the ingredients" },
  { id: "typed", icon: "⌨️", label: "Type it", hint: "Search 100+ ingredients" },
  { id: "checklist", icon: "✅", label: "Checklist", hint: "Tick off common staples" },
];

const SOURCE_ICON = { photo: "📷", typed: "⌨️", checklist: "✅" };

export default function PantryPage({ pantry, setPantry, onDone }) {
  const [method, setMethod] = useState("photo");
  const [error, setError] = useState(null);

  const run = async (promise) => {
    setError(null);
    try {
      const result = await promise;
      setPantry(result ?? (await api.pantry()));
    } catch (e) {
      setError(e.message);
    }
  };

  const add = (ids, source) => run(api.addToPantry(ids, source));
  const remove = (id) => run(api.removeFromPantry(id));
  const clear = () => {
    if (confirm("Remove everything from your pantry?")) run(api.clearPantry());
  };

  const inPantry = new Set(pantry.map((p) => p.ingredient_id));
  const byCategory = Object.groupBy
    ? Object.groupBy(pantry, (p) => p.category)
    : pantry.reduce((acc, p) => ((acc[p.category] ??= []).push(p), acc), {});

  return (
    <div className="pantry-layout">
      <section className="card">
        <h2>What's in your kitchen?</h2>
        <div className="method-picker" role="tablist" aria-label="How to add ingredients">
          {METHODS.map((m) => (
            <button
              key={m.id}
              role="tab"
              aria-selected={method === m.id}
              className={method === m.id ? "method active" : "method"}
              onClick={() => setMethod(m.id)}
            >
              <span className="method-icon" aria-hidden>{m.icon}</span>
              <span className="method-label">{m.label}</span>
              <span className="method-hint">{m.hint}</span>
            </button>
          ))}
        </div>

        {error && <p className="banner error" role="alert">{error}</p>}

        {method === "photo" && <PhotoScan inPantry={inPantry} onConfirm={(ids) => add(ids, "photo")} />}
        {method === "typed" && <TypeAhead taken={inPantry} onPick={(id) => add([id], "typed")} />}
        {method === "checklist" && (
          <Checklist inPantry={inPantry} onAdd={(id) => add([id], "checklist")} onRemove={remove} />
        )}
      </section>

      <aside className="card pantry-list">
        <div className="row spread">
          <h2>Your pantry</h2>
          {pantry.length > 0 && <button className="link" onClick={clear}>Clear all</button>}
        </div>
        {pantry.length === 0 ? (
          <p className="muted">Nothing yet. Add a few ingredients and we'll find meals you can make.</p>
        ) : (
          <>
            {Object.entries(byCategory).map(([category, items]) => (
              <div key={category} className="pantry-group">
                <h3>{category}</h3>
                <ul className="chips">
                  {items.map((item) => (
                    <li key={item.ingredient_id} className="chip">
                      <span title={`Added by ${item.source}`} aria-hidden>{SOURCE_ICON[item.source]}</span>
                      {item.name}
                      <button
                        className="chip-x"
                        aria-label={`Remove ${item.name}`}
                        onClick={() => remove(item.ingredient_id)}
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            <button className="primary wide" onClick={onDone}>
              See meals I can make →
            </button>
          </>
        )}
        <p className="muted small">Salt, pepper and water are always assumed.</p>
      </aside>
    </div>
  );
}
