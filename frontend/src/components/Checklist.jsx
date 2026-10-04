import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Checklist({ inPantry, onAdd, onRemove }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    api.commonIngredients().then(setItems).catch(() => {});
  }, []);

  return (
    <div className="checklist">
      {items.map((item) => {
        const checked = inPantry.has(item.id);
        return (
          <label key={item.id} className={checked ? "check checked" : "check"}>
            <input
              type="checkbox"
              checked={checked}
              onChange={() => (checked ? onRemove(item.id) : onAdd(item.id))}
            />
            {item.name}
          </label>
        );
      })}
    </div>
  );
}
