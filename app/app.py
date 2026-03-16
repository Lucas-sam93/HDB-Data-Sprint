import json
import datetime
import numpy as np
from pathlib import Path

from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

_MODEL_DIR = Path(__file__).parent / "models"

# ---------------------------------------------------------------------------
# Load classification model artefacts at startup
# ---------------------------------------------------------------------------
try:
    _rf_clf      = joblib.load(_MODEL_DIR / "rf_classifier.joblib")
    _clf_scaler  = joblib.load(_MODEL_DIR / "scaler_classifier.joblib")
    with open(_MODEL_DIR / "town_classes.json") as _f:
        _TOWN_CLASSES = json.load(_f)
    _clf_ready = True
except FileNotFoundError:
    _clf_ready = False  # Models not yet exported from notebook

# ---------------------------------------------------------------------------
# Load regression model artefacts at startup
# ---------------------------------------------------------------------------
try:
    _xgb_reg = joblib.load(_MODEL_DIR / "xgb_regressor.joblib")
    with open(_MODEL_DIR / "feature_columns.json") as _f:
        _FEATURE_COLS = json.load(_f)
    with open(_MODEL_DIR / "feature_medians.json") as _f:
        _FEATURE_MEDIANS = json.load(_f)
    _reg_ready = True
except FileNotFoundError:
    _reg_ready = False  # Run export cell in Regression_Models_Comparison.ipynb


@app.route("/")
def index():
    return render_template("index.html", active_tab="estimator")


@app.route("/predict", methods=["POST"])
def predict():
    if not _reg_ready:
        return render_template(
            "index.html",
            active_tab="estimator",
            price="—",
            price_note="Model not loaded — run the export cell in Regression_Models_Comparison.ipynb first.",
        )

    try:
        # --- Read form inputs (fall back to median when blank) ---
        floor_area  = float(request.form.get("floor_area_sqm") or _FEATURE_MEDIANS.get("floor_area_sqm", 90))
        mid_storey  = float(request.form.get("storey") or _FEATURE_MEDIANS.get("mid_storey", 8))
        hdb_age     = float(request.form.get("hdb_age") or 0)
        mrt_dist    = float(request.form.get("mrt_distance") or _FEATURE_MEDIANS.get("mrt_nearest_distance", 500))
        mall_dist   = float(request.form.get("mall_distance") or _FEATURE_MEDIANS.get("Mall_Nearest_Distance", 500))
        flat_type   = request.form.get("flat_type", "")
        town        = request.form.get("town", "")

        # Derive lease_commence_date from hdb_age (approximate)
        current_year = datetime.datetime.now().year
        lease_year   = current_year - int(hdb_age) if hdb_age else int(_FEATURE_MEDIANS.get("lease_commence_date", 1990))

        # --- Build feature vector filled with medians ---
        row = {col: _FEATURE_MEDIANS.get(col, 0.0) for col in _FEATURE_COLS}

        # Override numeric features from form
        row["floor_area_sqm"]        = floor_area
        row["mid_storey"]            = mid_storey
        row["lease_commence_date"]   = lease_year
        row["mrt_nearest_distance"]  = mrt_dist
        row["Mall_Nearest_Distance"] = mall_dist
        row["Tranc_Year"]            = current_year
        row["Tranc_Month"]           = datetime.datetime.now().month

        # One-hot encode flat_type
        if flat_type:
            col = f"flat_type_{flat_type}"
            if col in row:
                for c in _FEATURE_COLS:
                    if c.startswith("flat_type_"):
                        row[c] = 0.0
                row[col] = 1.0

        # One-hot encode town (also used as planning_area proxy)
        if town:
            town_col = f"town_{town}"
            if town_col in row:
                for c in _FEATURE_COLS:
                    if c.startswith("town_"):
                        row[c] = 0.0
                row[town_col] = 1.0
            planning_col = f"planning_area_{town}"
            if planning_col in row:
                for c in _FEATURE_COLS:
                    if c.startswith("planning_area_"):
                        row[c] = 0.0
                row[planning_col] = 1.0

        features = np.array([[row[col] for col in _FEATURE_COLS]])
        prediction = _xgb_reg.predict(features)[0]
        price_str = f"${prediction:,.0f}"
        note = "Estimate based on available inputs; other features use dataset medians."
    except Exception as e:
        price_str = "—"
        note = f"Error: {e}"

    return render_template(
        "index.html",
        active_tab="estimator",
        price=price_str,
        price_note=note,
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    if not _clf_ready:
        result = "Model not loaded — run the export cell in the classification notebook first."
        return render_template("index.html", active_tab="recommender", recommendation=result)

    try:
        mrt_dist    = float(request.form.get("mrt_distance") or 0)
        hawker_dist = float(request.form.get("hawker_distance") or 0)
        hdb_age     = float(request.form.get("hdb_age") or 0)
        max_floor   = float(request.form.get("max_floor_lvl") or 1)

        # Engineered features (mirror Classification_Models_Comparison.ipynb Step 3.5)
        total_distance  = mrt_dist + hawker_dist
        age_floor_ratio = hdb_age / max(max_floor, 1)

        # Feature order must match FEATURE_COLUMNS in notebook:
        # ['Hawker_Nearest_Distance', 'max_floor_lvl', 'mrt_nearest_distance',
        #  'hdb_age', 'total_distance', 'age_floor_ratio']
        features = np.array([[hawker_dist, max_floor, mrt_dist,
                               hdb_age, total_distance, age_floor_ratio]])
        features_scaled = _clf_scaler.transform(features)

        pred_idx  = _rf_clf.predict(features_scaled)[0]
        pred_town = _TOWN_CLASSES[pred_idx]
        result    = f"Recommended Town: {pred_town}"
    except Exception as e:
        result = f"Error: {e}"

    return render_template("index.html", active_tab="recommender", recommendation=result)


if __name__ == "__main__":
    import os
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", use_reloader=False)
