import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { GOALS, fmt } from "../nutrients.js";

export default function TodayPage() {
  const [today, setToday] = useState(null);
  const [error, setError] = useState(null);

  const refresh = useCallback(
    () => api.today().then(setToday).catch((e) => setError(e.message)),
    [],
  );
  useEffect(() => {
    refresh();
  }, [refresh]);

  const remove = async (id) => {
    await api.deleteMeal(id).catch((e) => setError(e.message));
    refresh();
  };

  if (!today) return <p className="muted">{error ?? "Loading…"}</p>;

  return (
    <div className="today-layout">
      <section className="card">
        <h2>Today's progress</h2>
        <p className="muted small">
          {new Date(today.day + "T00:00").toLocaleDateString(undefined, {
            weekday: "long", month: "long", day: "numeric",
          })}
        </p>
        <div className="progress-list">
          {GOALS.map((g) => (
            <ProgressBar key={g.key} goal={g} value={today.totals[g.key]} target={today.goals[g.key]} />
          ))}
        </div>

        <h3>Meals logged</h3>
        {today.meals.length === 0 ? (
          <p className="muted">Nothing logged yet. Open a recipe in Meal ideas and tap “I ate this”.</p>
        ) : (
          <ul className="meal-log">
            {today.meals.map((m) => (
              <li key={m.id}>
                <div>
                  <strong>{m.title}</strong>
                  <span className="muted small"> · {fmt(m.servings, 2)} serving{m.servings === 1 ? "" : "s"}</span>
                  <div className="muted small">
                    {fmt(m.nutrition.protein_g)}g protein · {fmt(m.nutrition.veg_servings, 1)} veg ·{" "}
                    {fmt(m.nutrition.iron_mg, 1)}mg iron · {fmt(m.nutrition.kcal)} kcal
                  </div>
                </div>
                <button className="link" onClick={() => remove(m.id)} aria-label={`Remove ${m.title}`}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="stack">
        <GoalsForm goals={today.goals} onSaved={refresh} />
        <WhyTheseGoals />
      </div>
    </div>
  );
}

function ProgressBar({ goal, value, target }) {
  const pct = Math.min(100, Math.round((100 * value) / target));
  const digits = goal.key === "veg_servings" || goal.key === "iron_mg" ? 1 : 0;
  return (
    <div className="progress">
      <div className="row spread">
        <span className="progress-label">{goal.label}</span>
        <span className="small">
          <strong>{fmt(value, digits)}</strong> / {fmt(target)} {goal.unit}
        </span>
      </div>
      <div
        className={`bar bar-${goal.key}`}
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${goal.label} ${pct}% of goal`}
      >
        <div style={{ width: `${pct}%` }} />
      </div>
      {goal.key === "kcal" && (
        <p className="muted small">Eating enough overall matters for regular cycles, so this is a floor to reach, not a limit.</p>
      )}
    </div>
  );
}

function GoalsForm({ goals, onSaved }) {
  const [draft, setDraft] = useState(goals);
  const [status, setStatus] = useState(null);

  const save = async (e) => {
    e.preventDefault();
    setStatus("saving");
    try {
      await api.saveGoals(draft);
      setStatus("saved");
      onSaved();
    } catch (err) {
      setStatus(err.message);
    }
  };

  return (
    <form className="card goals-form" onSubmit={save}>
      <h2>Daily goals</h2>
      {GOALS.map((g) => (
        <label key={g.key} className="goal-field">
          <span>{g.label}</span>
          <span className="input-unit">
            <input
              type="number"
              step={g.step}
              value={draft[g.key]}
              onChange={(e) => {
                setDraft({ ...draft, [g.key]: Number(e.target.value) });
                setStatus(null);
              }}
            />
            <span className="muted small">{g.unit}</span>
          </span>
        </label>
      ))}
      <button className="primary wide" disabled={status === "saving"}>Save goals</button>
      {status === "saved" && <p className="ok small" aria-live="polite">Saved ✓</p>}
      {status && !["saving", "saved"].includes(status) && <p className="error-text small">{status}</p>}
    </form>
  );
}

function WhyTheseGoals() {
  return (
    <section className="card why">
      <h2>Why these goals?</h2>
      <ul>
        <li>
          <strong>Enough energy overall.</strong> Regularly eating too little, especially alongside
          a lot of exercise, is one of the most common reasons periods become irregular or stop.
        </li>
        <li>
          <strong>Protein</strong> supports recovery, steady energy and fullness. Around 1.2–1.6 g per kg
          of body weight suits most active women.
        </li>
        <li>
          <strong>Iron.</strong> Periods mean regular iron loss. The recommended intake for women aged
          19–50 is 18 mg a day, and plant iron absorbs better alongside vitamin C (peppers, citrus, tomatoes).
        </li>
        <li>
          <strong>Fiber and veggies</strong> support gut health and steadier blood sugar, which is
          especially helpful for people with PCOS.
        </li>
        <li>
          <strong>Healthy fats</strong> from olive oil, nuts, seeds, avocado and oily fish are part of a
          balanced diet that supports hormone health.
        </li>
      </ul>
      <p className="muted small">
        This app is a nutrition planner, not medical advice. If your cycles are often irregular,
        stop for 3+ months, or are very painful, see a doctor. Common causes like PCOS and
        thyroid conditions are very treatable.
      </p>
    </section>
  );
}
