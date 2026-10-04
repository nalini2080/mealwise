import { useEffect, useState } from "react";
import { api } from "../api.js";
import { fmt } from "../nutrients.js";
import Modal from "./Modal.jsx";

export default function ShoppingList({ recipeIds, onClose, onClear }) {
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const key = recipeIds.join(",");
  useEffect(() => {
    api.shoppingList(key.split(",")).then(setItems).catch((e) => setError(e.message));
  }, [key]);

  const copy = async () => {
    const text = items.map((i) => `- ${i.name} (${fmt(i.grams)} g)`).join("\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
  };

  return (
    <Modal title="Shopping list" onClose={onClose}>
      <h2>Shopping list</h2>
      {error && <p className="banner error">{error}</p>}
      {items === null ? (
        <p className="muted">Loading…</p>
      ) : items.length === 0 ? (
        <p>You already have everything for these recipes.</p>
      ) : (
        <>
          <ul className="shopping">
            {items.map((i) => (
              <li key={i.ingredient_id}>
                <span><strong>{i.name}</strong> <span className="muted">· {fmt(i.grams)} g</span></span>
                <span className="muted small">for {i.for_recipes.join(", ")}</span>
              </li>
            ))}
          </ul>
          <div className="row gap">
            <button className="primary" onClick={copy}>{copied ? "Copied ✓" : "Copy list"}</button>
            <button className="secondary" onClick={onClear}>Clear selection</button>
          </div>
        </>
      )}
    </Modal>
  );
}
