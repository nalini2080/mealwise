import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function TypeAhead({ taken, takenLabel = "in pantry", onPick, placeholder, autoFocus = true }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [active, setActive] = useState(0);
  const [justAdded, setJustAdded] = useState(null);

  // Debounce so we query once the user pauses, not on every keystroke.
  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      api.searchIngredients(q).then((r) => {
        if (!cancelled) {
          setResults(r);
          setActive(0);
        }
      }).catch(() => {});
    }, 150);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  const pick = (item) => {
    if (!item || taken.has(item.id)) return;
    onPick(item.id, item);
    setJustAdded(item.name);
    setQuery("");
    setResults([]);
  };

  const onKeyDown = (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      pick(results[active]);
    }
  };

  return (
    <div className="typeahead">
      <label htmlFor="ingredient-search" className="sr-only">Search ingredients</label>
      <input
        id="ingredient-search"
        className="search"
        placeholder={placeholder ?? "Try “spinach”, “garbanzo” or even “brocoli”"}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={onKeyDown}
        autoComplete="off"
        autoFocus={autoFocus}
        role="combobox"
        aria-expanded={results.length > 0}
        aria-controls="ingredient-options"
      />
      {results.length > 0 && (
        <ul className="options" id="ingredient-options" role="listbox">
          {results.map((item, i) => {
            const owned = taken.has(item.id);
            return (
              <li
                key={item.id}
                role="option"
                aria-selected={i === active}
                className={[i === active && "active", owned && "disabled"].filter(Boolean).join(" ")}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => {
                  e.preventDefault();
                  pick(item);
                }}
              >
                <span>{item.name}</span>
                <span className="muted small">{owned ? takenLabel : item.category}</span>
              </li>
            );
          })}
        </ul>
      )}
      {query.trim() && results.length === 0 && (
        <p className="muted small">No matches yet — keep typing.</p>
      )}
      {justAdded && <p className="muted small" aria-live="polite">Added {justAdded}.</p>}
    </div>
  );
}
