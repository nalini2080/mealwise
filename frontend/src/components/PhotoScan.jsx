import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";

// Upload -> Gemini detects ingredients -> user reviews and edits -> confirm.
// Low-confidence guesses start unchecked so the user opts in to them.
export default function PhotoScan({ inPantry, onConfirm }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | scanning | review | error
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(new Set());
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  const choose = (f) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      setError("Please choose an image file.");
      setStatus("error");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setStatus("idle");
    setError(null);
  };

  const scan = async () => {
    setStatus("scanning");
    setError(null);
    try {
      const res = await api.scanPhoto(file);
      setResult(res);
      setSelected(
        new Set(
          res.detected
            .filter((d) => d.confidence !== "low" && !inPantry.has(d.ingredient_id))
            .map((d) => d.ingredient_id),
        ),
      );
      setStatus("review");
    } catch (e) {
      setError(e.message);
      setStatus("error");
    }
  };

  const toggle = (id) =>
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  const confirm = async () => {
    await onConfirm([...selected]);
    setFile(null);
    setPreview(null);
    setResult(null);
    setStatus("idle");
  };

  return (
    <div className="photo-scan">
      <div
        className={dragging ? "dropzone dragging" : "dropzone"}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          choose(e.dataTransfer.files[0]);
        }}
        onClick={() => inputRef.current.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current.click()}
      >
        {preview ? (
          <img src={preview} alt="Your fridge or pantry" className="preview" />
        ) : (
          <div className="dropzone-empty">
            <span className="big-icon" aria-hidden>📷</span>
            <strong>Drop a photo of your fridge or pantry</strong>
            <span className="muted">or click to choose one (on a phone you can use the camera)</span>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          capture="environment"
          hidden
          onChange={(e) => choose(e.target.files[0])}
        />
      </div>

      {file && status !== "review" && (
        <button className="primary wide" onClick={scan} disabled={status === "scanning"}>
          {status === "scanning" ? (
            <><span className="spinner" aria-hidden /> Looking for ingredients…</>
          ) : (
            "Find ingredients"
          )}
        </button>
      )}

      {status === "error" && (
        <p className="banner error" role="alert">
          {error} You can still add ingredients by typing or with the checklist.
        </p>
      )}

      {status === "review" && result && (
        <div className="review">
          <h3>We spotted {result.detected.length} ingredients — check what's right</h3>
          {result.detected.length === 0 && (
            <p className="muted">Nothing recognizable. Try a closer, brighter photo.</p>
          )}
          <ul className="review-list">
            {result.detected.map((d) => {
              const owned = inPantry.has(d.ingredient_id);
              return (
                <li key={d.ingredient_id}>
                  <label className={owned ? "disabled" : undefined}>
                    <input
                      type="checkbox"
                      checked={owned || selected.has(d.ingredient_id)}
                      disabled={owned}
                      onChange={() => toggle(d.ingredient_id)}
                    />
                    <span>{d.name}</span>
                    {d.label.toLowerCase() !== d.name && <span className="muted small">(saw “{d.label}”)</span>}
                    {owned ? (
                      <span className="badge">in pantry</span>
                    ) : (
                      <span className={`badge conf-${d.confidence}`}>{d.confidence}</span>
                    )}
                  </label>
                </li>
              );
            })}
          </ul>
          {result.unmatched.length > 0 && (
            <p className="muted small">
              Not in our ingredient list yet: {result.unmatched.join(", ")}.
            </p>
          )}
          <button className="primary wide" disabled={selected.size === 0} onClick={confirm}>
            Add {selected.size} to pantry
          </button>
        </div>
      )}
    </div>
  );
}
