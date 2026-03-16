# HDB Predictor UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Full UI redesign of the HDB Resale Price Predictor — two-column layout, DM Serif Display typography, async fetch submission, sequenced result animations, and all competitor UX patterns from the spec.

**Architecture:** Three-file change. `app.py` gets minimal content-negotiation JSON endpoints (no logic change). `style.css` is a full rewrite keeping the same CSS custom-property token approach. `index.html` is a full rewrite with fetch-based JS replacing the page-reload form submission.

**Tech Stack:** Flask/Jinja2, vanilla CSS (custom properties, grid, clamp), vanilla JS (fetch, FormData, requestAnimationFrame), Google Fonts (DM Serif Display + Inter)

**Spec:** `docs/superpowers/specs/2026-03-16-hdb-predictor-redesign.md`

---

## Chunk 1: Backend JSON Endpoints

### Task 1: Add JSON response support to `/predict`

**Files:**
- Modify: `app/app.py`

- [ ] **Step 1: Open `app/app.py` and locate the `/predict` route (around line 79)**

- [ ] **Step 2: Add `jsonify` to the Flask import at line 6**

Change:
```python
from flask import Flask, render_template, request
```
To:
```python
from flask import Flask, render_template, request, jsonify
```

- [ ] **Step 3: Add JSON content-negotiation block at the end of the `predict()` function, before the final `return render_template(...)`**

Find this block near the end of `predict()`:
```python
    return render_template(
        "index.html",
        active_tab="estimator",
        price=price_str,
        price_raw=int(prediction) if isinstance(prediction, (int, float)) else 0,
        price_low=price_low_str,
        price_high=price_high_str,
        used_inputs=used_inputs,
        price_note=note,
    )
```

Replace with:
```python
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "price": price_str,
            "price_raw": int(prediction) if isinstance(prediction, (int, float)) else 0,
            "price_low": price_low_str,
            "price_high": price_high_str,
            "used_inputs": used_inputs,
            "price_note": note,
        })
    return render_template(
        "index.html",
        active_tab="estimator",
        price=price_str,
        price_raw=int(prediction) if isinstance(prediction, (int, float)) else 0,
        price_low=price_low_str,
        price_high=price_high_str,
        used_inputs=used_inputs,
        price_note=note,
    )
```

- [ ] **Step 4: Verify the model-not-loaded early return also handles JSON**

Find the early return block:
```python
    if not _reg_ready:
        return render_template(
            "index.html",
            active_tab="estimator",
            price="—",
            price_note="Model not loaded — run the export cell in Regression_Models_Comparison.ipynb first.",
        )
```

Replace with:
```python
    if not _reg_ready:
        msg = "Model not loaded — run the export cell in Regression_Models_Comparison.ipynb first."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"price": "—", "price_raw": 0, "price_low": "—", "price_high": "—", "used_inputs": [], "price_note": msg})
        return render_template("index.html", active_tab="estimator", price="—", price_note=msg)
```

- [ ] **Step 5: Test manually**

Start the app: `python app/app.py`
Run in a separate terminal:
```bash
curl -s -X POST http://127.0.0.1:5000/predict \
  -H "Accept: application/json" \
  -d "flat_type=4+ROOM&floor_area_sqm=90"
```
Expected: JSON response `{"price": "$...", "price_raw": ..., ...}`

Also verify the HTML path still works by visiting `http://127.0.0.1:5000/` in a browser and submitting the form normally.

- [ ] **Step 6: Commit**
```bash
git add app/app.py
git commit -m "feat: add JSON content negotiation to /predict endpoint"
```

---

### Task 2: Add JSON response support to `/recommend`

**Files:**
- Modify: `app/app.py`

- [ ] **Step 1: Find the model-not-loaded early return in `recommend()`**

Find:
```python
    if not _clf_ready:
        result = "Model not loaded — run the export cell in the classification notebook first."
        return render_template("index.html", active_tab="recommender", recommendation=result)
```

Replace with:
```python
    if not _clf_ready:
        msg = "Model not loaded — run the export cell in the classification notebook first."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"rec_town": "—", "rec_desc": "", "error": msg})
        return render_template("index.html", active_tab="recommender", recommendation=msg)
```

- [ ] **Step 2: Add JSON content-negotiation at the end of `recommend()`**

Find the final return:
```python
    return render_template(
        "index.html",
        active_tab="recommender",
        recommendation=result,
        rec_town=pred_town or "—",
        rec_desc=rec_desc,
    )
```

Replace with:
```python
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "rec_town": pred_town or "—",
            "rec_desc": rec_desc,
        })
    return render_template(
        "index.html",
        active_tab="recommender",
        recommendation=result,
        rec_town=pred_town or "—",
        rec_desc=rec_desc,
    )
```

- [ ] **Step 3: Test manually**
```bash
curl -s -X POST http://127.0.0.1:5000/recommend \
  -H "Accept: application/json" \
  -d "mrt_distance=500&hawker_distance=300&hdb_age=20&max_floor_lvl=10"
```
Expected: JSON response `{"rec_town": "...", "rec_desc": "..."}`

- [ ] **Step 4: Commit**
```bash
git add app/app.py
git commit -m "feat: add JSON content negotiation to /recommend endpoint"
```

---

## Chunk 2: CSS Redesign

### Task 3: Write new `style.css` — tokens, reset, base, typography

**Files:**
- Rewrite: `app/static/style.css`

- [ ] **Step 1: Replace the entire contents of `app/static/style.css` with the following**

```css
/* ── Reset ─────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Tokens ────────────────────────────────────────────────── */
:root {
  --bg:          #f8fafc;
  --surface:     #ffffff;
  --border:      #e5e7eb;
  --accent:      #E05206;
  --accent-hi:   #f26522;
  --navy:        #0f172a;
  --text:        #0f172a;
  --muted:       #64748b;
  --dim:         #9ca3af;
  --input-bg:    #ffffff;
  --success:     #16a34a;
  --r-card:      16px;
  --r-input:     10px;
  --ease:        150ms ease-out;
  --ease-in:     150ms ease-in;
}
[data-theme="dark"] {
  --bg:          #0f172a;
  --surface:     #1e293b;
  --border:      #334155;
  --accent:      #E05206;
  --accent-hi:   #f26522;
  --text:        #e2e8f0;
  --muted:       #94a3b8;
  --dim:         #64748b;
  --input-bg:    rgba(15,23,42,0.8);
  --success:     #4ade80;
}

/* ── Base ──────────────────────────────────────────────────── */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  background: var(--bg);
  color: var(--text);
  min-height: 100dvh;
  transition: background var(--ease), color var(--ease);
}

/* ── Display font ──────────────────────────────────────────── */
.font-display {
  font-family: 'DM Serif Display', Georgia, serif;
}

/* ── Skip link ─────────────────────────────────────────────── */
.skip-link {
  position: absolute;
  top: -999px;
  left: 0;
  background: var(--accent);
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 0 0 8px 0;
  z-index: 1000;
  font-size: 0.875rem;
}
.skip-link:focus { top: 0; }

/* ── Focus ring ────────────────────────────────────────────── */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* ── Hero ──────────────────────────────────────────────────── */
.hero {
  position: relative;
  background: var(--navy);
  overflow: hidden;
  padding: 0 2rem;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.hero::before {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: var(--accent);
  filter: blur(80px);
  opacity: 0.18;
  top: -100px; left: -60px;
  pointer-events: none;
}
.hero-brand {
  font-family: 'DM Serif Display', Georgia, serif;
  color: var(--accent);
  font-size: 0.85rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}
.hero-centre {
  flex: 1;
  text-align: center;
}
.hero-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 400;
  color: #fff;
  line-height: 1.2;
  letter-spacing: -0.01em;
}
.hero-subtitle {
  color: var(--muted);
  font-size: 0.82rem;
  margin-top: 0.2rem;
}
.hero-trust {
  color: #94a3b8;
  font-size: 0.75rem;
  margin-top: 0.2rem;
  display: none; /* shown only ≥1024px via media query below */
}

/* ── Theme toggle ──────────────────────────────────────────── */
.theme-toggle {
  background: transparent;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.4rem 0.6rem;
  cursor: pointer;
  color: #94a3b8;
  transition: border-color var(--ease), color var(--ease);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0;
}
.theme-toggle:hover { border-color: var(--accent); color: var(--accent); }
.theme-toggle svg { width: 18px; height: 18px; display: block; }
.icon-sun, .icon-moon { transition: opacity var(--ease); }

/* ── Page body layout ──────────────────────────────────────── */
.page-body {
  display: block; /* single column default; two-column at ≥1024px */
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.25rem;
  gap: 2rem;
}

/* ── Card ──────────────────────────────────────────────────── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 2rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 24px rgba(0,0,0,0.04);
  transition: border-color var(--ease);
}
.card-title {
  font-family: 'DM Serif Display', Georgia, serif;
  color: var(--text);
  font-size: 1.375rem;
  font-weight: 400;
  letter-spacing: -0.01em;
  margin-bottom: 0.25rem;
}
.card-hint {
  color: var(--muted);
  font-size: 0.875rem;
  margin-bottom: 1.75rem;
}

/* ── Form grid ─────────────────────────────────────────────── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}
.field-full { grid-column: 1 / -1; }

.field label {
  display: block;
  color: var(--text);
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
}

/* ── Text inputs & selects ─────────────────────────────────── */
.text-input {
  background: var(--input-bg);
  border: 1.5px solid var(--border);
  border-radius: var(--r-input);
  color: var(--text);
  font-family: inherit;
  font-size: 0.9rem;
  padding: 0.65rem 0.9rem;
  width: 100%;
  min-height: 44px;
  outline: none;
  transition: border-color var(--ease), box-shadow var(--ease);
  -webkit-appearance: none;
}
.text-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(224,82,6,0.15);
}
select.text-input {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23E05206' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.9rem center;
  padding-right: 2.2rem;
  cursor: pointer;
  text-transform: capitalize;
}

/* ── Pill group ────────────────────────────────────────────── */
.pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.pill-radio { display: none; }
.pill-label {
  cursor: pointer;
  border: 1.5px solid var(--border);
  border-radius: 999px;
  padding: 0.4rem 1rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--muted);
  transition: all var(--ease);
  user-select: none;
}
.pill-label:hover { border-color: var(--accent); color: var(--accent); }
.pill-radio:checked + .pill-label {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

/* ── Typeahead ─────────────────────────────────────────────── */
.typeahead-wrap { position: relative; }
.typeahead-drop {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  max-height: 220px;
  overflow-y: auto;
  z-index: 100;
  display: none;
}
.typeahead-drop.open { display: block; }
.drop-item {
  padding: 0.6rem 0.9rem;
  font-size: 0.875rem;
  cursor: pointer;
  color: var(--text);
  transition: background var(--ease), color var(--ease);
  border-radius: 6px;
}
.drop-item:hover,
.drop-item.focused { background: rgba(224,82,6,0.08); color: var(--accent); }

/* ── More details toggle ───────────────────────────────────── */
.details-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.25rem 0;
  margin-bottom: 1rem;
}
.details-toggle svg {
  width: 16px; height: 16px;
  transition: transform 250ms ease-out;
  flex-shrink: 0;
}
.details-toggle[aria-expanded="true"] svg { transform: rotate(180deg); }

.details-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 180ms ease-in; /* collapse: faster, ease-in */
}
.details-content.open {
  max-height: 400px;
  transition: max-height 250ms ease-out; /* expand */
}

/* ── Sliders ───────────────────────────────────────────────── */
.slider-field { display: flex; flex-direction: column; gap: 0.4rem; }
.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--dim);
}
input[type="range"] {
  -webkit-appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  outline: none;
  cursor: pointer;
  /* background set dynamically via JS fill */
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--surface);
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  cursor: pointer;
}
input[type="range"]::-moz-range-thumb {
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--surface);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.slider-val {
  text-align: center;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent);
}

/* ── Submit button ─────────────────────────────────────────── */
.btn-primary {
  background: var(--accent);
  border: none;
  border-radius: var(--r-input);
  color: #fff;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  min-height: 48px;
  padding: 0.85rem 2rem;
  width: 100%;
  transition: background var(--ease), box-shadow var(--ease), transform 100ms ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.btn-primary:hover {
  background: var(--accent-hi);
  box-shadow: 0 4px 20px rgba(224,82,6,0.35);
}
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

/* CSS spinner */
.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 600ms linear infinite;
  display: none;
  flex-shrink: 0;
}
.btn-primary.loading .btn-spinner { display: block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Recommender toggle link ───────────────────────────────── */
.rec-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.8rem;
  padding: 0.75rem 0 0;
  text-align: left;
  transition: color var(--ease);
}
.rec-toggle:hover { color: var(--accent); }
.rec-toggle svg { width: 14px; height: 14px; flex-shrink: 0; transition: transform 300ms ease-out; }
.rec-toggle[aria-expanded="true"] svg { transform: rotate(180deg); }

.rec-section {
  max-height: 0;
  overflow: hidden;
  transition: max-height 220ms ease-in; /* collapse: faster, ease-in */
}
.rec-section.open {
  max-height: 500px;
  transition: max-height 300ms ease-out; /* expand */
}
.rec-section-inner {
  border-top: 1px solid var(--border);
  margin-top: 1rem;
  padding-top: 1.25rem;
}
.rec-section-inner .card-title { font-size: 1.1rem; margin-bottom: 0.2rem; }
.rec-section-inner .card-hint { margin-bottom: 1.25rem; }

/* ── Result panel ──────────────────────────────────────────── */
.result-panel {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--r-card);
  padding: 2rem;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: border-color 150ms ease-out;
}
.result-panel.has-result {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(224,82,6,0.06);
  justify-content: flex-start;
}

/* Empty state */
.result-empty { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
.result-empty svg { width: 48px; height: 48px; color: var(--dim); }
.result-empty-title {
  color: var(--text);
  font-size: 1rem;
  font-weight: 600;
}
.result-empty-hint { color: var(--muted); font-size: 0.85rem; }
.result-panel.has-result .result-empty { display: none; }

/* Result content */
.result-content { display: none; width: 100%; }
.result-panel.has-result .result-content { display: block; }

.result-label {
  color: var(--muted);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}
.result-price {
  font-family: 'DM Serif Display', Georgia, serif;
  color: var(--accent);
  font-size: 2.5rem;
  font-weight: 400;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
  margin-bottom: 0.4rem;
}
.result-town {
  font-family: 'DM Serif Display', Georgia, serif;
  color: var(--accent);
  font-size: 2rem;
  font-weight: 400;
  line-height: 1.2;
  margin-bottom: 0.3rem;
}
.result-range { color: var(--muted); font-size: 0.85rem; margin-bottom: 1rem; }
.result-town-desc { color: var(--muted); font-size: 0.875rem; margin-bottom: 1rem; }

/* Chips */
.result-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: center;
  margin-bottom: 0.75rem;
  min-height: 1.5rem;
}
.chip {
  background: rgba(224,82,6,0.08);
  color: var(--accent);
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
}
.chip-muted {
  background: transparent;
  color: var(--muted);
  font-size: 0.75rem;
  padding: 0.25rem 0;
  font-style: italic;
}

/* Reassurance + CTA */
.result-reassurance {
  color: var(--muted);
  font-size: 0.78rem;
  margin-bottom: 1.25rem;
}
.result-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0 0 1rem;
}
.result-cta-label {
  color: var(--muted);
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}
.result-cta-btn {
  background: none;
  border: 1.5px solid var(--border);
  border-radius: 999px;
  color: var(--text);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 0.4rem 1.1rem;
  transition: border-color var(--ease), color var(--ease);
}
.result-cta-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Fade-in animation classes (JS-added) */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: none; }
}
.fade-in { animation: fadeUp 200ms ease-out both; }

/* ── Footer ────────────────────────────────────────────────── */
.footer {
  text-align: center;
  padding: 1.5rem 1.25rem;
  color: var(--dim);
  font-size: 0.75rem;
  border-top: 1px solid var(--border);
}

/* ── Responsive ────────────────────────────────────────────── */
@media (min-width: 1024px) {
  .hero-trust { display: block; }

  .page-body {
    display: grid;
    grid-template-columns: 55fr 45fr;
    align-items: start;
  }

  .result-col {
    position: sticky;
    top: 2rem;
  }
}

@media (max-width: 767px) {
  .hero { height: auto; padding: 1rem 1.25rem; }
  .hero-brand { display: none; } /* hide brand wordmark on mobile to save space */
  .form-grid { grid-template-columns: 1fr; }
  .card { padding: 1.25rem; }
  .result-price { font-size: 2rem; }
  .result-town  { font-size: 1.5rem; }

  input[type="range"]::-webkit-slider-thumb { width: 24px; height: 24px; }
  input[type="range"]::-moz-range-thumb     { width: 24px; height: 24px; }
  input[type="range"] { height: 6px; }
}

/* ── Reduced motion ────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .result-panel,
  .result-price,
  .result-range,
  .result-chips,
  .result-reassurance,
  .result-divider,
  .result-cta-label,
  .result-cta-btn,
  .details-content,
  .rec-section,
  .btn-spinner,
  .fade-in {
    animation: none !important;
    transition: none !important;
  }
}
```

- [ ] **Step 2: Save the file and verify it loads without errors by opening the Flask app in a browser**

---

### Task 4: Commit CSS

- [ ] **Step 1: Commit**
```bash
git add app/static/style.css
git commit -m "feat: full CSS redesign — two-column layout, DM Serif Display, result panel, animations"
```

---

## Chunk 3: HTML + JS Rewrite

### Task 5: Rewrite `index.html` — structure, hero, fonts

**Files:**
- Rewrite: `app/templates/index.html`

- [ ] **Step 1: Replace the entire contents of `app/templates/index.html` with the following**

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HDB Resale Price Predictor &middot; WOW! Real Estate</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}?v=4" />
</head>
<body>

  <a class="skip-link" href="#main">Skip to main content</a>

  <!-- ── Hero Bar ─────────────────────────────────────────── -->
  <header class="hero" role="banner">
    <div class="hero-brand">WOW! Real Estate</div>
    <div class="hero-centre">
      <h1 class="hero-title">HDB Resale Price Predictor</h1>
      <p class="hero-subtitle">AI-powered estimates &middot; Singapore public housing</p>
      <p class="hero-trust">Estimate based on real Singapore HDB resale data</p>
    </div>
    <button class="theme-toggle" id="themeToggle" aria-label="Switch to dark mode">
      <!-- Sun icon (shown in dark mode) -->
      <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
      </svg>
      <!-- Moon icon (shown in light mode) -->
      <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round" aria-hidden="true">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    </button>
  </header>

  <!-- ── Two-column body ──────────────────────────────────── -->
  <div class="page-body" id="main">

    <!-- ── LEFT: Form column ──────────────────────────────── -->
    <div class="form-col">

      <!-- Price Estimator form -->
      <!-- action/method retained for no-JS progressive enhancement; fetch intercepts when JS is available -->
      <form class="card" id="estimatorForm" action="/predict" method="POST" novalidate>
        <h2 class="card-title">Property Details</h2>
        <p class="card-hint">Fill in what you know &mdash; all fields are optional.</p>

        <div class="form-grid">

          <!-- Flat Type: pill selector -->
          <div class="field field-full">
            <label>Flat Type</label>
            <div class="pill-group" role="group" aria-label="Flat type">
              <input type="radio" name="flat_type" id="ft_1r" value="1 ROOM" class="pill-radio">
              <label for="ft_1r" class="pill-label">1 Room</label>
              <input type="radio" name="flat_type" id="ft_2r" value="2 ROOM" class="pill-radio">
              <label for="ft_2r" class="pill-label">2 Room</label>
              <input type="radio" name="flat_type" id="ft_3r" value="3 ROOM" class="pill-radio">
              <label for="ft_3r" class="pill-label">3 Room</label>
              <input type="radio" name="flat_type" id="ft_4r" value="4 ROOM" class="pill-radio">
              <label for="ft_4r" class="pill-label">4 Room</label>
              <input type="radio" name="flat_type" id="ft_5r" value="5 ROOM" class="pill-radio">
              <label for="ft_5r" class="pill-label">5 Room</label>
              <input type="radio" name="flat_type" id="ft_ex" value="EXECUTIVE" class="pill-radio">
              <label for="ft_ex" class="pill-label">Executive</label>
              <input type="radio" name="flat_type" id="ft_mg" value="MULTI-GENERATION" class="pill-radio">
              <label for="ft_mg" class="pill-label">Multi-Gen</label>
            </div>
          </div>

          <!-- Town: typeahead -->
          <div class="field">
            <label for="town_input">Town</label>
            <div class="typeahead-wrap">
              <input type="text" id="town_input" class="text-input"
                placeholder="Search town..." autocomplete="off"
                role="combobox" aria-autocomplete="list"
                aria-controls="town_drop" aria-expanded="false" />
              <input type="hidden" name="town" id="town_value" />
              <div class="typeahead-drop" id="town_drop"
                role="listbox" aria-label="Town suggestions"></div>
            </div>
          </div>

          <!-- Floor Area -->
          <div class="field">
            <label for="floor_area_sqm">Floor Area (sqm)</label>
            <input class="text-input" type="number" name="floor_area_sqm" id="floor_area_sqm"
              placeholder="e.g. 90" min="1" inputmode="numeric" autocomplete="off" />
          </div>

          <!-- Storey -->
          <div class="field">
            <label for="storey">Storey</label>
            <input class="text-input" type="number" name="storey" id="storey"
              placeholder="e.g. 8" min="1" inputmode="numeric" autocomplete="off" />
          </div>

          <!-- HDB Age -->
          <div class="field">
            <label for="hdb_age">HDB Age (years)</label>
            <input class="text-input" type="number" name="hdb_age" id="hdb_age"
              placeholder="e.g. 25" min="0" inputmode="numeric" autocomplete="off" />
          </div>

        </div><!-- /form-grid -->

        <!-- More details toggle -->
        <button type="button" class="details-toggle" id="detailsToggle"
          aria-expanded="false" aria-controls="detailsContent">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          More details
        </button>

        <!-- Secondary inputs (collapsed) -->
        <div class="details-content" id="detailsContent" aria-hidden="true">
          <div class="form-grid">

            <!-- Flat Model -->
            <div class="field field-full">
              <label for="flat_model">Flat Model</label>
              <select class="text-input" name="flat_model" id="flat_model" autocomplete="off">
                <option value="">&#8212; select &#8212;</option>
                <option title="Standard renovation scheme">Improved</option>
                <option>New Generation</option>
                <option>Model A</option>
                <option title="Higher-spec fittings and finishes">Premium Apartment</option>
                <option>Simplified</option>
                <option>Standard</option>
                <option title="Two-storey flat">Maisonette</option>
                <option>Apartment</option>
                <option>Terrace</option>
                <option>Adjoined Flat</option>
                <option>Type S1</option>
                <option>Type S2</option>
                <option>Model A2</option>
                <option title="Design, Build and Sell Scheme — private developer built">DBSS</option>
                <option>Special</option>
              </select>
            </div>

            <!-- MRT Distance: slider -->
            <div class="field slider-field">
              <label for="mrt_distance">MRT Distance</label>
              <input type="range" name="mrt_distance" id="mrt_distance"
                min="100" max="2000" step="50" value="500" />
              <div class="slider-labels">
                <span>Nearby &lt;500m</span><span>~1 km</span><span>Far &gt;2 km</span>
              </div>
              <div class="slider-val" id="mrt_val">500 m</div>
            </div>

            <!-- Mall Distance: slider -->
            <div class="field slider-field">
              <label for="mall_distance">Mall Distance</label>
              <input type="range" name="mall_distance" id="mall_distance"
                min="100" max="2000" step="50" value="500" />
              <div class="slider-labels">
                <span>Nearby &lt;500m</span><span>~1 km</span><span>Far &gt;2 km</span>
              </div>
              <div class="slider-val" id="mall_val">500 m</div>
            </div>

          </div>
        </div><!-- /details-content -->

        <button type="submit" class="btn-primary" id="estimatorBtn">
          <span class="btn-spinner" aria-hidden="true"></span>
          <span class="btn-label">Estimate Price &rarr;</span>
        </button>

        <!-- Recommender toggle -->
        <!-- NOTE: This button is inside estimatorForm but has type="button" so it will not trigger form submit.
             The recSection it controls is a sibling of the form (outside it) — valid HTML. -->
        <button type="button" class="rec-toggle" id="recToggle"
          aria-expanded="false" aria-controls="recSection">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          Not sure which town? Find your ideal neighbourhood
        </button>

      </form><!-- /estimatorForm -->

      <!-- Recommender section (expandable) -->
      <div class="rec-section" id="recSection" aria-hidden="true">
        <div class="rec-section-inner">
          <!-- action/method retained for no-JS progressive enhancement -->
          <form class="card" id="recommenderForm" action="/recommend" method="POST" novalidate
            style="border:none;padding:0;box-shadow:none;background:transparent;">
            <h2 class="card-title">Find Your Ideal Town</h2>
            <p class="card-hint">Enter your preferences and we&rsquo;ll recommend the best neighbourhood.</p>

            <div class="form-grid">

              <!-- MRT Distance: slider -->
              <div class="field slider-field">
                <label for="rec_mrt">MRT Distance</label>
                <input type="range" name="mrt_distance" id="rec_mrt"
                  min="100" max="2000" step="50" value="500" />
                <div class="slider-labels">
                  <span>Nearby &lt;500m</span><span>~1 km</span><span>Far &gt;2 km</span>
                </div>
                <div class="slider-val" id="rec_mrt_val">500 m</div>
              </div>

              <!-- Hawker Distance: slider -->
              <div class="field slider-field">
                <label for="hawker_distance">Hawker Centre Distance</label>
                <input type="range" name="hawker_distance" id="hawker_distance"
                  min="50" max="1500" step="50" value="300" />
                <div class="slider-labels">
                  <span>Nearby &lt;300m</span><span>~700m</span><span>Far &gt;1.5 km</span>
                </div>
                <div class="slider-val" id="hawker_val">300 m</div>
              </div>

              <!-- HDB Age -->
              <div class="field">
                <label for="rec_hdb_age">HDB Age (years)</label>
                <input class="text-input" type="number" name="hdb_age" id="rec_hdb_age"
                  placeholder="e.g. 20" min="0" inputmode="numeric" autocomplete="off" />
              </div>

              <!-- Max Floor Level -->
              <div class="field">
                <label for="max_floor_lvl">Max Floor Level</label>
                <input class="text-input" type="number" name="max_floor_lvl" id="max_floor_lvl"
                  placeholder="e.g. 12" min="1" inputmode="numeric" autocomplete="off" />
              </div>

            </div>

            <button type="submit" class="btn-primary" id="recommenderBtn">
              <span class="btn-spinner" aria-hidden="true"></span>
              <span class="btn-label">Get Recommendation &rarr;</span>
            </button>

          </form>
        </div>
      </div><!-- /rec-section -->

    </div><!-- /form-col -->

    <!-- ── RIGHT: Result column ────────────────────────────── -->
    <div class="result-col">
      <div class="result-panel" id="resultPanel" role="alert" aria-live="polite" aria-atomic="true">

        <!-- Empty state -->
        <div class="result-empty" id="resultEmpty">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <div class="result-empty-title">Your estimate will appear here</div>
          <div class="result-empty-hint">Fill in the form on the left to get started</div>
        </div>

        <!-- Result content (hidden until fetch returns) -->
        <div class="result-content" id="resultContent">
          <div class="result-label" id="resultLabel">Estimated Resale Price</div>
          <div class="result-price" id="resultPrice"></div>
          <div class="result-town" id="resultTown" style="display:none"></div>
          <div class="result-range" id="resultRange"></div>
          <div class="result-town-desc" id="resultTownDesc" style="display:none"></div>
          <div class="result-chips" id="resultChips"></div>
          <div class="result-reassurance" id="resultReassurance">
            Estimate based on real Singapore HDB resale data
          </div>
          <hr class="result-divider" id="resultDivider" />
          <div class="result-cta-label" id="resultCtaLabel"></div>
          <button type="button" class="result-cta-btn" id="resultCtaBtn"></button>
        </div>

      </div>
    </div><!-- /result-col -->

  </div><!-- /page-body -->

  <footer class="footer">
    &copy; 2026 WOW! Real Estate &middot; For informational purposes only
  </footer>

  <script>
  // ── Theme toggle ──────────────────────────────────────────────
  (function() {
    const html   = document.documentElement;
    const btn    = document.getElementById('themeToggle');
    const sun    = btn.querySelector('.icon-sun');
    const moon   = btn.querySelector('.icon-moon');
    const saved  = localStorage.getItem('theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    function applyTheme(t) {
      html.setAttribute('data-theme', t);
      sun.style.opacity  = t === 'dark' ? '1' : '0';
      moon.style.opacity = t === 'dark' ? '0' : '1';
      btn.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
    applyTheme(saved);

    btn.addEventListener('click', () => {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      applyTheme(next);
    });
  })();

  // ── Town typeahead with keyboard navigation ───────────────────
  (function() {
    const TOWNS = [
      "ANG MO KIO","BEDOK","BISHAN","BUKIT BATOK","BUKIT MERAH","BUKIT PANJANG",
      "BUKIT TIMAH","CENTRAL AREA","CHOA CHU KANG","CLEMENTI","GEYLANG","HOUGANG",
      "JURONG EAST","JURONG WEST","KALLANG/WHAMPOA","MARINE PARADE","PASIR RIS",
      "PUNGGOL","QUEENSTOWN","SEMBAWANG","SENGKANG","SERANGOON","TAMPINES",
      "TOA PAYOH","WOODLANDS","YISHUN"
    ];
    const input  = document.getElementById('town_input');
    const hidden = document.getElementById('town_value');
    const drop   = document.getElementById('town_drop');
    let focusIdx = -1;

    function getItems() { return drop.querySelectorAll('.drop-item'); }

    function renderDrop(q) {
      const matches = q ? TOWNS.filter(t => t.includes(q.toUpperCase())) : TOWNS;
      drop.innerHTML = matches.map((t, i) =>
        `<div class="drop-item" role="option" id="town-opt-${i}" data-val="${t}" aria-selected="false">${t}</div>`
      ).join('');
      drop.classList.toggle('open', matches.length > 0);
      input.setAttribute('aria-expanded', matches.length > 0 ? 'true' : 'false');
      focusIdx = -1;
    }

    function setFocus(idx) {
      const items = getItems();
      items.forEach((el, i) => {
        el.classList.toggle('focused', i === idx);
        el.setAttribute('aria-selected', i === idx ? 'true' : 'false');
      });
      if (idx >= 0) input.setAttribute('aria-activedescendant', `town-opt-${idx}`);
      else input.removeAttribute('aria-activedescendant');
    }

    function selectItem(val) {
      input.value  = val;
      hidden.value = val;
      input.style.borderColor = 'var(--accent)';
      drop.classList.remove('open');
      input.setAttribute('aria-expanded', 'false');
      focusIdx = -1;
    }

    input.addEventListener('focus', () => renderDrop(input.value));
    input.addEventListener('input', () => { hidden.value = ''; renderDrop(input.value); });

    input.addEventListener('keydown', e => {
      const items = getItems();
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        focusIdx = Math.min(focusIdx + 1, items.length - 1);
        setFocus(focusIdx);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        focusIdx = Math.max(focusIdx - 1, -1);
        setFocus(focusIdx);
      } else if (e.key === 'Enter' && focusIdx >= 0) {
        e.preventDefault();
        selectItem(items[focusIdx].dataset.val);
      } else if (e.key === 'Escape') {
        drop.classList.remove('open');
        input.setAttribute('aria-expanded', 'false');
        focusIdx = -1;
      }
    });

    drop.addEventListener('click', e => {
      const item = e.target.closest('.drop-item');
      if (item) selectItem(item.dataset.val);
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !drop.contains(e.target)) {
        drop.classList.remove('open');
        input.setAttribute('aria-expanded', 'false');
      }
    });
  })();

  // ── Slider fill ───────────────────────────────────────────────
  function updateSliderFill(slider) {
    const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background =
      `linear-gradient(to right, var(--accent) 0%, var(--accent) ${pct}%, var(--border) ${pct}%, var(--border) 100%)`;
  }

  function bindSlider(id, valId) {
    const s = document.getElementById(id);
    const d = document.getElementById(valId);
    if (!s || !d) return;
    updateSliderFill(s);
    d.textContent = s.value + ' m';
    s.addEventListener('input', () => {
      updateSliderFill(s);
      d.textContent = s.value + ' m';
    });
  }

  bindSlider('mrt_distance',   'mrt_val');
  bindSlider('mall_distance',  'mall_val');
  bindSlider('rec_mrt',        'rec_mrt_val');
  bindSlider('hawker_distance','hawker_val');

  // ── More details toggle ───────────────────────────────────────
  (function() {
    const btn     = document.getElementById('detailsToggle');
    const content = document.getElementById('detailsContent');
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !expanded);
      content.setAttribute('aria-hidden', expanded);
      content.classList.toggle('open', !expanded);
      // Re-init slider fills when revealed
      if (!expanded) {
        ['mrt_distance','mall_distance'].forEach(id => {
          const s = document.getElementById(id);
          if (s) updateSliderFill(s);
        });
      }
    });
  })();

  // ── Recommender toggle ────────────────────────────────────────
  (function() {
    const btn     = document.getElementById('recToggle');
    const section = document.getElementById('recSection');
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !expanded);
      section.setAttribute('aria-hidden', expanded);
      section.classList.toggle('open', !expanded);
      if (!expanded) {
        // Re-init recommender sliders
        ['rec_mrt','hawker_distance'].forEach(id => {
          const s = document.getElementById(id);
          if (s) updateSliderFill(s);
        });
      }
    });
  })();

  // ── Result panel helpers ──────────────────────────────────────
  const panel       = document.getElementById('resultPanel');
  const resultContent = document.getElementById('resultContent');
  const resultEmpty = document.getElementById('resultEmpty');

  function showResult() {
    panel.classList.add('has-result');
    // Scroll result into view on tablet/mobile
    if (window.innerWidth < 1024) {
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function fadeInEl(el, delayMs) {
    if (reducedMotion) { el.style.opacity = '1'; return; }
    el.style.opacity = '0';
    setTimeout(() => {
      el.classList.add('fade-in');
      el.style.opacity = '';
    }, delayMs);
  }

  function countUp(el, target) {
    if (reducedMotion || target === 0) {
      el.textContent = '$' + Math.round(target).toLocaleString();
      return;
    }
    const dur = 300;
    const t0  = performance.now();
    function tick(now) {
      const p = Math.min((now - t0) / dur, 1);
      const e = 1 - Math.pow(1 - p, 3); // ease-out cubic
      el.textContent = '$' + Math.round(target * e).toLocaleString();
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // ── Render estimator result ───────────────────────────────────
  function renderEstimatorResult(data) {
    const priceEl       = document.getElementById('resultPrice');
    const townEl        = document.getElementById('resultTown');
    const rangeEl       = document.getElementById('resultRange');
    const townDescEl    = document.getElementById('resultTownDesc');
    const chipsEl       = document.getElementById('resultChips');
    const reassuranceEl = document.getElementById('resultReassurance');
    const dividerEl     = document.getElementById('resultDivider');
    const ctaLabelEl    = document.getElementById('resultCtaLabel');
    const ctaBtn        = document.getElementById('resultCtaBtn');
    const labelEl       = document.getElementById('resultLabel');

    // Reset visibility
    labelEl.textContent = 'Estimated Resale Price';
    priceEl.style.display    = '';
    townEl.style.display     = 'none';
    rangeEl.style.display    = '';
    townDescEl.style.display = 'none';

    // Border flash
    panel.style.borderColor = 'var(--accent)';

    // t=100ms: count up price
    setTimeout(() => countUp(priceEl, data.price_raw || 0), 100);

    // t=400ms: range + chips
    setTimeout(() => {
      rangeEl.textContent = `Range: ${data.price_low} \u2013 ${data.price_high}`;
      fadeInEl(rangeEl, 0);

      chipsEl.innerHTML = '';
      if (data.used_inputs && data.used_inputs.length > 0) {
        data.used_inputs.forEach(inp => {
          const chip = document.createElement('span');
          chip.className = 'chip';
          chip.textContent = inp;
          chipsEl.appendChild(chip);
        });
      } else {
        const muted = document.createElement('span');
        muted.className = 'chip-muted';
        muted.textContent = 'Using dataset medians \u2014 add inputs above for a personalised estimate.';
        chipsEl.appendChild(muted);
      }
      fadeInEl(chipsEl, 0);
    }, 400);

    // t=600ms: reassurance
    setTimeout(() => {
      reassuranceEl.textContent = 'Estimate based on real Singapore HDB resale data';
      fadeInEl(reassuranceEl, 0);
    }, 600);

    // t=900ms: divider + CTA
    setTimeout(() => {
      ctaLabelEl.textContent = 'Want to explore this further?';
      ctaBtn.textContent = 'Find your ideal town \u2192';
      ctaBtn.onclick = () => {
        const recBtn = document.getElementById('recToggle');
        if (recBtn.getAttribute('aria-expanded') !== 'true') recBtn.click();
        recBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      };
      fadeInEl(dividerEl, 0);
      fadeInEl(ctaLabelEl, 50);
      fadeInEl(ctaBtn, 100);
    }, 900);

    showResult();
  }

  // ── Render recommender result ─────────────────────────────────
  function renderRecommenderResult(data) {
    const priceEl       = document.getElementById('resultPrice');
    const townEl        = document.getElementById('resultTown');
    const rangeEl       = document.getElementById('resultRange');
    const townDescEl    = document.getElementById('resultTownDesc');
    const chipsEl       = document.getElementById('resultChips');
    const reassuranceEl = document.getElementById('resultReassurance');
    const dividerEl     = document.getElementById('resultDivider');
    const ctaLabelEl    = document.getElementById('resultCtaLabel');
    const ctaBtn        = document.getElementById('resultCtaBtn');
    const labelEl       = document.getElementById('resultLabel');

    labelEl.textContent      = 'Recommended Town';
    priceEl.style.display    = 'none';
    rangeEl.style.display    = 'none';
    townEl.style.display     = '';
    townDescEl.style.display = '';

    panel.style.borderColor = 'var(--accent)';

    setTimeout(() => {
      townEl.textContent     = data.rec_town || '\u2014';
      townDescEl.textContent = data.rec_desc || '';
      fadeInEl(townEl, 0);
    }, 100);

    setTimeout(() => {
      chipsEl.innerHTML = '';
      fadeInEl(townDescEl, 0);
    }, 300);

    setTimeout(() => {
      reassuranceEl.textContent = 'Estimate based on real Singapore HDB resale data';
      fadeInEl(reassuranceEl, 0);
    }, 500);

    setTimeout(() => {
      ctaLabelEl.textContent = 'Want to estimate a price instead?';
      ctaBtn.textContent     = 'Price Estimator \u2192';
      ctaBtn.onclick = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('estimatorForm').querySelector('.btn-primary').focus();
      };
      fadeInEl(dividerEl, 0);
      fadeInEl(ctaLabelEl, 50);
      fadeInEl(ctaBtn, 100);
    }, 700);

    showResult();
  }

  // ── Fetch submit helpers ──────────────────────────────────────
  // NOTE: On reset, the button always shows "Re-estimate →" / "Get Recommendation →"
  // even on the first submit. This matches the spec (Section 4: "resets to Re-estimate →").
  // On fetch error the label also resets — no estimate is shown, but the button is usable.
  function setLoading(btn, loading) {
    btn.disabled = loading;
    btn.classList.toggle('loading', loading);
    btn.querySelector('.btn-label').textContent = loading
      ? (btn.id === 'estimatorBtn' ? 'Estimating\u2026' : 'Finding\u2026')
      : (btn.id === 'estimatorBtn' ? 'Re-estimate \u2192' : 'Get Recommendation \u2192');
  }

  // ── Estimator form submit ─────────────────────────────────────
  // NOTE: setLoading(btn, false) fires immediately after fetch resolves (~200-500ms),
  // while the animation chain runs for ~900ms. This is intentional — the button
  // becomes interactive again while the result animates in.
  document.getElementById('estimatorForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('estimatorBtn');
    setLoading(btn, true);
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(this),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      renderEstimatorResult(data);
    } catch (err) {
      console.error(err);
      // Show error state in result panel
      panel.classList.add('has-result');
      document.getElementById('resultLabel').textContent = 'Something went wrong';
      document.getElementById('resultPrice').textContent = '\u2014';
      document.getElementById('resultPrice').style.display = '';
      document.getElementById('resultRange').textContent = 'Please try again.';
      document.getElementById('resultChips').innerHTML = '';
      document.getElementById('resultReassurance').textContent = '';
    } finally {
      setLoading(btn, false);
    }
  });

  // ── Recommender form submit ───────────────────────────────────
  document.getElementById('recommenderForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('recommenderBtn');
    setLoading(btn, true);
    try {
      const res = await fetch('/recommend', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(this),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      renderRecommenderResult(data);
    } catch (err) {
      console.error(err);
      panel.classList.add('has-result');
      document.getElementById('resultLabel').textContent = 'Something went wrong';
      document.getElementById('resultTown').textContent = '\u2014';
      document.getElementById('resultTown').style.display = '';
      document.getElementById('resultRange').style.display = 'none';
      document.getElementById('resultReassurance').textContent = 'Please try again.';
    } finally {
      setLoading(btn, false);
    }
  });
  </script>

</body>
</html>
```

- [ ] **Step 2: Save the file**

- [ ] **Step 2b: Verify the page loads without errors before testing interactions**

Start the Flask app: `python app/app.py`
Open `http://127.0.0.1:5000/` and check:
- Page loads without a 500 error
- Browser console shows no JS exceptions
- Hero bar is visible with navy background
- Form card is visible with pill selector and town input

Fix any syntax errors before continuing to Step 3.

- [ ] **Step 3: Start the Flask app and verify interactions**
```bash
python app/app.py
```
Open `http://127.0.0.1:5000/` and check:
- Hero bar renders correctly with navy background and orange glow
- Two-column layout on desktop (≥1024px)
- Single column on tablet/mobile (resize browser)
- "More details" toggle expands/collapses the secondary inputs
- "Not sure which town?" toggle expands/collapses the Recommender form
- Theme toggle switches between light and dark (no emoji — SVG icons)
- Town typeahead filters and supports arrow key navigation
- Sliders show filled track (orange left of thumb, grey right)
- Submit button shows spinner and "Estimating…" during fetch (if models loaded)
- Result panel updates in place — no page reload
- Price counts up from 0 on result
- Chips, reassurance line, and CTA fade in sequentially after price

- [ ] **Step 4: Commit**
```bash
git add app/templates/index.html
git commit -m "feat: full HTML/JS redesign — two-column layout, async fetch, sequenced result animation"
```

---

## Chunk 4: Final verification

### Task 6: Cross-browser and responsive check

- [ ] **Step 1: Test at 375px width (mobile)**
  - Form grid is single column
  - Hero is compact
  - After submit, page scrolls to result panel

- [ ] **Step 2: Test at 768px width (tablet)**
  - Single column layout
  - Result panel below form (not sticky)

- [ ] **Step 3: Test at 1200px width (desktop)**
  - Two-column layout visible
  - Result panel is sticky (stays in view when scrolling the form)

- [ ] **Step 4: Test dark mode**
  - Click theme toggle: colours swap correctly
  - Refresh page: dark mode persists (localStorage)
  - Test in a browser with OS dark mode set: page loads in dark mode without localStorage entry

- [ ] **Step 5: Test keyboard navigation**
  - Tab to town input, type partial name, use ArrowDown/ArrowUp to navigate, Enter to select
  - Tab to "More details" button, press Enter — section expands
  - Tab to "Not sure which town?" button, press Enter — Recommender section expands

- [ ] **Step 6: Test with models not loaded**
  - If `app/models/` is empty, submit the estimator
  - Expected: result panel shows `—` price with the model-not-loaded note (returned from JSON endpoint)

- [ ] **Step 7: Final commit**
```bash
git add .
git commit -m "chore: verified redesign — cross-browser, responsive, keyboard nav, dark mode"
```
