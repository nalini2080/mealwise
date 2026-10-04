import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import PantryPage from "./components/PantryPage.jsx";
import MealsPage from "./components/MealsPage.jsx";
import TodayPage from "./components/TodayPage.jsx";
import AllergiesPage from "./components/AllergiesPage.jsx";

const TABS = [
  { id: "pantry", label: "My pantry" },
  { id: "meals", label: "Meal ideas" },
  { id: "today", label: "Today" },
  { id: "allergies", label: "Allergies" },
];

export default function App() {
  const [tab, setTab] = useState("pantry");
  const [pantry, setPantry] = useState([]);
  const [error, setError] = useState(null);

  const refreshPantry = useCallback(
    () => api.pantry().then(setPantry).catch((e) => setError(e.message)),
    [],
  );
  useEffect(() => {
    refreshPantry();
  }, [refreshPantry]);

  return (
    <div className="app">
      <header className="masthead">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="36" height="36" />
          <div>
            <h1>MealWise</h1>
            <p>Meals from what you have, tailored to what your body needs.</p>
          </div>
        </div>
        <nav className="tabs" aria-label="Sections">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={tab === t.id ? "tab active" : "tab"}
              aria-current={tab === t.id ? "page" : undefined}
              onClick={() => setTab(t.id)}
            >
              {t.label}
              {t.id === "pantry" && pantry.length > 0 && (
                <span className="count">{pantry.length}</span>
              )}
            </button>
          ))}
        </nav>
      </header>

      {error && (
        <div className="banner error" role="alert">
          {error} — is the API running?
          <button className="link" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <main>
        {tab === "pantry" && (
          <PantryPage pantry={pantry} setPantry={setPantry} onDone={() => setTab("meals")} />
        )}
        {tab === "meals" && (
          <MealsPage
            pantryCount={pantry.length}
            onLogged={() => setTab("today")}
            onEditAllergies={() => setTab("allergies")}
          />
        )}
        {tab === "today" && <TodayPage />}
        {tab === "allergies" && <AllergiesPage />}
      </main>

      <footer className="footer">
        MealWise is a nutrition planner, not medical advice. Nutrition values are estimates
        from USDA FoodData Central.
      </footer>
    </div>
  );
}
