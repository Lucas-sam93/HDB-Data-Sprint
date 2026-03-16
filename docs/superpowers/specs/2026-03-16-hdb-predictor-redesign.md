# HDB Resale Price Predictor — Full Redesign Spec
**Date:** 2026-03-16
**Project:** WOW! Real Estate — HDB Resale Price Predictor
**Scope:** Full redesign of `app/templates/index.html` + `app/static/style.css` + minimal `app/app.py` changes (JSON endpoints only)

---

## 1. Goal

Redesign the HDB Resale Price Predictor web app to match the UX quality of leading Singapore property platforms (SRX X-Value, HomerAI, PropertyGuru, Propsbit) while preserving and extending the current app's strengths: dark mode, accessible markup, semantic CSS tokens, and no-login friction.

**Tone:** Approachable but polished. Warm and friendly for everyday HDB buyers; credible enough for WOW! management presentation.

---

## 2. Layout & Structure

### Desktop (≥1024px) — Two-column split
- **Left column (55%):** Slim hero bar + form panel
- **Right column (45%):** Result panel — `position: sticky; top: 2rem`, always in eyeline

### Tablet (768–1023px) — Single column
- Result panel drops below the form, loses `sticky`
- Page auto-scrolls to result panel on submit

### Mobile (<768px) — Stacked, touch-optimised
- Hero bar slim (≈80px tall)
- Form grid collapses to 1-column
- Result panel appears below submit on submit
- Page auto-scrolls to result panel

### Page structure
```
[Hero Bar — full width]
[Two-column body]
  Left:  Form panel
  Right: Result panel (sticky on desktop)
[Footer strip]
```

---

## 3. Hero Bar

- **Height:** ~120px desktop, ~80px mobile
- **Background:** Deep navy (`#0f172a`) with subtle orange radial glow top-left
- **Layout:** Three-zone single row on desktop; stacks to two rows on tablet/mobile
  - Left: "WOW! REAL ESTATE" in DM Serif Display, small caps, orange
  - Centre: Title + subtitle only (trust stat line hidden on tablet/mobile to prevent overflow)
  - Right: SVG theme toggle (sun/moon — no emoji)
- **Trust stat line** ("Estimate based on real Singapore HDB resale data") visible only on desktop (≥1024px); hidden via `display: none` at tablet/mobile breakpoints

### Content
```
HDB Resale Price Predictor
AI-powered estimates · Singapore public housing
Estimate based on real Singapore HDB resale data   ← desktop only
```

- Title: DM Serif Display, white, `clamp(1.5rem, 3vw, 2rem)`
- Subtitle: Inter, muted
- Trust stat: Inter, `0.8rem`, slightly brighter than muted — plain English, no jargon

---

## 4. Form Panel (Left Column)

### Navigation
- Tab bar removed entirely
- "Price Estimator" is the default and only visible form on page load
- Recommender entry point is a soft secondary link below the submit button:
  > *Not sure which town? Find your ideal neighbourhood →*
- Clicking this link expands the Recommender form **inline within the left column**, directly below the link, on all breakpoints
- The right column result panel remains visible and unchanged while the Recommender form is expanded
- Clicking the link a second time collapses the Recommender form

### Primary inputs — always visible
| Field | Component |
|---|---|
| Flat Type | Pill selector (existing, unchanged) |
| Town | Typeahead with keyboard navigation |
| Floor Area (sqm) | Number input |
| Storey | Number input |
| HDB Age (years) | Number input |

### Secondary inputs — collapsed by default
Revealed by "More details ▾" toggle (orange, small chevron icon).

| Field | Component |
|---|---|
| Flat Model | Select — title-cased options, `title` attribute for jargon terms (DBSS, MSCP etc.) |
| MRT Distance | Range slider with filled track |
| Mall Distance | Range slider with filled track |

### Submit button
- Full width, orange, `min-height: 48px`
- On click: JS intercepts submit event, sends `fetch()` POST to `/predict` (see Section 15), button text → "Estimating…" + CSS spinner, button disabled
- On response: button resets to "Re-estimate →", result panel updates in place (no page reload)

### Recommender form (expandable, inline below submit)
- Expands via `max-height: 0 → 500px` transition (fixed value, larger than content), `300ms ease-out`
- Collapses via `max-height: 500px → 0`, `220ms ease-in`
- Fields: MRT Distance (slider), Hawker Distance (slider), HDB Age (number), Max Floor Level (number)
- Own submit button: "Get Recommendation →" with same `fetch()` loading pattern, POSTs to `/recommend`
- Result appears in the right column result panel (replaces Estimator result if one exists), or below the Recommender form on tablet/mobile

---

## 5. Result Panel (Right Column — Sticky)

### Empty state (desktop right column / below form on tablet+mobile)
```
[SVG house outline icon — muted colour]

Your estimate will
appear here

Fill in the form on the left
to get started
```
- Border: `1px solid var(--border)`, `border-radius: 16px`
- Background: `#f8fafc` light / `#1e293b` dark

### Estimator result reveal — sequenced animation (JS-driven, post-fetch)
| Time | Event | Duration |
|---|---|---|
| t=0ms | Panel border transitions to orange | 150ms |
| t=100ms | Price counts up from 0 to final value | 300ms ease-out cubic |
| t=400ms | Range + input chips fade in | 200ms |
| t=600ms | Reassurance line fades in | 200ms |
| t=900ms | Separator + secondary CTA fades in | 200ms |

### Estimator result content
```
ESTIMATED RESALE PRICE
$485,000

Range: $436,500 – $533,500

[4 Room] [Ang Mo Kio] [90 sqm]   ← chips, or fallback text if no inputs

Estimate based on real Singapore HDB resale data

──────────────────────────────
Want to explore this further?
[Find your ideal town →]
```

- Price: DM Serif Display, `2.5rem`, orange, `font-variant-numeric: tabular-nums`
- Range: Inter, muted, `0.85rem`
- Chips: existing `.chip` styles, unchanged
- Reassurance: Inter, `0.8rem`, muted — **no model jargon, no technical stats**
- Secondary CTA scrolls to and expands the Recommender form in the left column

### Input chips — always rendered
The chips `div` renders unconditionally. When `used_inputs` is empty (no fields filled), it displays:
> *Using dataset medians — add inputs above for a personalised estimate.*

When `used_inputs` is non-empty, it renders the chips as now.

### Recommender result content (same panel, replaces Estimator result)
```
RECOMMENDED TOWN

TAMPINES

Non-mature · East

──────────────────────────────
Want to estimate a price instead?
[Price Estimator →]
```
- Town name: DM Serif Display, `2rem`, orange
- Description: Inter, muted, `0.875rem`
- Secondary CTA scrolls back to the top of the estimator form

### prefers-reduced-motion
- Count-up skips to final value instantly
- All fades run at 100ms instead of 200ms
- `max-height` transitions run at 50ms (effectively instant)

---

## 6. Typography System

| Role | Font | Weight | Usage |
|---|---|---|---|
| Display | DM Serif Display | 400 | Hero title, result price, result town, card headings |
| UI | Inter | 300–800 | All labels, inputs, body copy, buttons |

Google Fonts import:
```css
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600;700;800&display=swap');
```

---

## 7. Color Token System

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--bg` | `#f8fafc` | `#0f172a` | Page background |
| `--surface` | `#ffffff` | `#1e293b` | Cards, panels |
| `--border` | `#e5e7eb` | `#334155` | Borders, dividers |
| `--accent` | `#E05206` | `#E05206` | Orange — brand colour |
| `--accent-hi` | `#f26522` | `#f26522` | Hover state |
| `--navy` | `#0f172a` | — | Hero bar background only |
| `--text` | `#0f172a` | `#e2e8f0` | Body text |
| `--muted` | `#64748b` | `#94a3b8` | Secondary text |
| `--dim` | `#9ca3af` | `#64748b` | Placeholder, tertiary |
| `--success` | `#16a34a` | `#4ade80` | Reserved for future use |

---

## 8. Responsive Breakpoints

| Breakpoint | Layout change |
|---|---|
| `≥1024px` | Two-column split, result panel sticky, hero trust stat visible |
| `768–1023px` | Single column, result below form, no sticky, hero trust stat hidden |
| `<768px` | 1-column form grid, slim hero, auto-scroll to result, hero trust stat hidden |

---

## 9. Animation & Interaction Specification

Reduced-motion handled via targeted CSS (not universal selector):
```css
@media (prefers-reduced-motion: reduce) {
  .result-panel,
  .result-price,
  .result-range,
  .result-chips,
  .result-note,
  .result-cta,
  .secondary-form,
  .details-content {
    animation: none !important;
    transition: none !important;
  }
}
```
Count-up animation checks `window.matchMedia('(prefers-reduced-motion: reduce)').matches` in JS and skips to final value if true.

| Interaction | Duration | Easing | Notes |
|---|---|---|---|
| "More details" expand | 250ms | ease-out | `max-height: 0 → 400px` |
| "More details" collapse | 180ms | ease-in | Exit faster than enter |
| Recommender expand | 300ms | ease-out | `max-height: 0 → 500px` |
| Recommender collapse | 220ms | ease-in | |
| Chevron rotation | 150ms | ease-out | 0° → 180° |
| Result border → orange | 150ms | ease-out | |
| Price count-up | 300ms | cubic ease-out | Shortened from current 800ms intentionally |
| Chips/range/text fades | 200ms each | ease-out | Staggered per reveal table in Section 5 |
| Submit scale on active | 100ms | ease | `scale(0.98)` → `scale(1)` on release |
| Theme toggle icon swap | 150ms | ease | Opacity crossfade |
| Global colour transition | 150ms | ease | Via `var(--ease)` on bg/border/color |

---

## 10. Accessibility Requirements

- Skip link retained (`<a class="skip-link" href="#main">`)
- ARIA tablist/tabpanel roles removed (no tabs in redesign); replaced with ARIA landmark regions (`<main>`, `<header>`, `<section>`)
- `aria-live="polite" aria-atomic="true"` retained on result panel
- `aria-expanded="false/true"` on "More details" toggle and Recommender toggle, updated by JS on click
- Typeahead upgraded with full keyboard navigation:
  - `ArrowDown` / `ArrowUp` — move through dropdown items
  - `Enter` — select focused item
  - `Escape` — close dropdown, return focus to input
  - `aria-activedescendant` on input pointing to focused item id
  - `role="listbox"` on dropdown, `role="option"` on each item
- All SVG icons: `aria-hidden="true"` if decorative; `aria-label` if functional (theme toggle)
- Theme toggle: `aria-label="Switch to dark mode"` / `"Switch to light mode"` updated dynamically
- `prefers-color-scheme` sets default theme on load
- Focus-visible rings: `outline: 2px solid var(--accent); outline-offset: 2px` on all interactive elements
- Minimum touch targets: `44px` height on all inputs; `48px` on submit buttons

---

## 11. Slider Enhancement

Range inputs get a filled track via JS-updated CSS gradient:
```js
function updateSliderFill(slider) {
  const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
  slider.style.background = `linear-gradient(to right,
    var(--accent) 0%, var(--accent) ${pct}%,
    var(--border) ${pct}%, var(--border) 100%)`;
}
```
Called on `input` event and on page load for all range inputs.

---

## 12. Theme Toggle

- OS preference detected on load:
```js
const saved = localStorage.getItem('theme') ||
  (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
```
- Toggle button uses inline SVG sun/moon icons (Lucide `sun` and `moon`), no emoji
- Both SVGs present in DOM; active one at `opacity: 1`, inactive at `opacity: 0`; crossfade via `transition: opacity 150ms`

---

## 13. What Is Not Changing

- Prediction and recommendation ML logic — no changes
- CSS token naming convention — extended, not replaced
- Pill selector for Flat Type — kept as-is, it outperforms competitor dropdowns
- `font-variant-numeric: tabular-nums` on price — kept
- `inputmode="numeric"` on number fields — kept
- `font-display: swap` via Google Fonts — kept

---

## 14. Files Changed

| File | Change type |
|---|---|
| `app/templates/index.html` | Full rewrite |
| `app/static/style.css` | Full rewrite |
| `app/app.py` | Minimal: `/predict` and `/recommend` return JSON when `Accept: application/json` header is present; existing HTML render path kept as fallback |

---

## 15. Backend Change — JSON Endpoints

The two-column layout with sequenced result animations requires async form submission (no page reload). The `/predict` and `/recommend` routes must support JSON responses.

### Pattern (content negotiation — no breaking change)
```python
from flask import request, jsonify

@app.route("/predict", methods=["POST"])
def predict():
    # ... existing logic unchanged ...
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "price": price_str,
            "price_raw": int(prediction),
            "price_low": price_low_str,
            "price_high": price_high_str,
            "used_inputs": used_inputs,
            "price_note": note,
        })
    return render_template("index.html", ...)  # existing path unchanged
```

Same pattern for `/recommend`, returning `rec_town` and `rec_desc`.

The existing HTML render path is fully preserved — the app still works without JS (progressive enhancement).

### JS fetch pattern (in index.html)
```js
form.addEventListener('submit', async e => {
  e.preventDefault();
  btn.disabled = true;
  btn.textContent = 'Estimating…';
  const res = await fetch('/predict', {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
    body: new FormData(form),
  });
  const data = await res.json();
  updateResultPanel(data);   // triggers sequenced animation
  btn.disabled = false;
  btn.textContent = 'Re-estimate →';
});
```
