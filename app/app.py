import json
import datetime
import numpy as np
from pathlib import Path

from flask import Flask, render_template, request, jsonify
import joblib

_TOWN_DESCRIPTIONS = {
    "ANG MO KIO":      "Mature estate · Central-North",
    "BEDOK":           "Mature estate · East",
    "BISHAN":          "Mature estate · Central",
    "BUKIT BATOK":     "Mature estate · West",
    "BUKIT MERAH":     "Mature estate · Central-South",
    "BUKIT PANJANG":   "Non-mature · West",
    "BUKIT TIMAH":     "Mature estate · Central",
    "CENTRAL AREA":    "City centre · Central",
    "CHOA CHU KANG":   "Non-mature · West",
    "CLEMENTI":        "Mature estate · West",
    "GEYLANG":         "Mature estate · Central-East",
    "HOUGANG":         "Mature estate · North-East",
    "JURONG EAST":     "Non-mature · West",
    "JURONG WEST":     "Non-mature · West",
    "KALLANG/WHAMPOA": "Mature estate · Central",
    "MARINE PARADE":   "Mature estate · East",
    "PASIR RIS":       "Non-mature · East",
    "PUNGGOL":         "Non-mature · North-East",
    "QUEENSTOWN":      "Mature estate · Central",
    "SEMBAWANG":       "Non-mature · North",
    "SENGKANG":        "Non-mature · North-East",
    "SERANGOON":       "Mature estate · North-East",
    "TAMPINES":        "Non-mature · East",
    "TOA PAYOH":       "Mature estate · Central",
    "WOODLANDS":       "Non-mature · North",
    "YISHUN":          "Non-mature · North",
}

_HERE = Path(__file__).parent

app = Flask(
    __name__,
    template_folder=str(_HERE / "templates"),
    static_folder=str(_HERE / "static"),
)

_MODEL_DIR = _HERE / "models"

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
    _clf_ready = False

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
    _reg_ready = False


@app.route("/")
def index():
    return render_template("index.html", active_tab="estimator")


@app.route("/predict", methods=["POST"])
def predict():
    if not _reg_ready:
        msg = "Model not loaded — run the export cell in Regression_Models_Comparison.ipynb first."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"price": "—", "price_raw": 0, "price_low": "—", "price_high": "—", "used_inputs": [], "price_note": msg})
        return render_template("index.html", active_tab="estimator", price="—", price_note=msg)

    prediction = 0
    try:
        floor_area = float(request.form.get("floor_area_sqm") or _FEATURE_MEDIANS.get("floor_area_sqm", 90))
        mid_storey = float(request.form.get("storey") or _FEATURE_MEDIANS.get("mid_storey", 8))
        hdb_age    = float(request.form.get("hdb_age") or 0)
        mrt_dist   = float(request.form.get("mrt_distance") or _FEATURE_MEDIANS.get("mrt_nearest_distance", 500))
        mall_dist  = float(request.form.get("mall_distance") or _FEATURE_MEDIANS.get("Mall_Nearest_Distance", 500))
        flat_type  = request.form.get("flat_type", "")
        town       = request.form.get("town", "")

        current_year = datetime.datetime.now().year
        lease_year   = current_year - int(hdb_age) if hdb_age else int(_FEATURE_MEDIANS.get("lease_commence_date", 1990))

        row = {col: _FEATURE_MEDIANS.get(col, 0.0) for col in _FEATURE_COLS}
        row["floor_area_sqm"]        = floor_area
        row["mid_storey"]            = mid_storey
        row["lease_commence_date"]   = lease_year
        row["mrt_nearest_distance"]  = mrt_dist
        row["Mall_Nearest_Distance"] = mall_dist
        row["Tranc_Year"]            = current_year
        row["Tranc_Month"]           = datetime.datetime.now().month

        if flat_type:
            col = f"flat_type_{flat_type}"
            if col in row:
                for c in _FEATURE_COLS:
                    if c.startswith("flat_type_"):
                        row[c] = 0.0
                row[col] = 1.0

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

        features   = np.array([[row[col] for col in _FEATURE_COLS]])
        prediction = _xgb_reg.predict(features)[0]

        price_str      = f"${prediction:,.0f}"
        price_low_str  = f"${prediction * 0.90:,.0f}"
        price_high_str = f"${prediction * 1.10:,.0f}"
        note = "Estimate based on available inputs; other features use dataset medians."

        used_inputs = []
        if request.form.get("flat_type"):      used_inputs.append(request.form.get("flat_type").title())
        if request.form.get("town"):           used_inputs.append(request.form.get("town").title())
        if request.form.get("floor_area_sqm"): used_inputs.append(f"{request.form.get('floor_area_sqm')} sqm")
        if request.form.get("storey"):         used_inputs.append(f"Storey {request.form.get('storey')}")
        if request.form.get("hdb_age"):        used_inputs.append(f"{request.form.get('hdb_age')}yr old")

    except Exception as e:
        price_str = price_low_str = price_high_str = "—"
        used_inputs = []
        note = f"Error: {e}"

    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "price": price_str,
            "price_raw": int(float(prediction)),
            "price_low": price_low_str,
            "price_high": price_high_str,
            "used_inputs": used_inputs,
            "price_note": note,
        })
    return render_template(
        "index.html",
        active_tab="estimator",
        price=price_str,
        price_raw=int(float(prediction)),
        price_low=price_low_str,
        price_high=price_high_str,
        used_inputs=used_inputs,
        price_note=note,
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    if not _clf_ready:
        msg = "Model not loaded — run the export cell in the classification notebook first."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"rec_town": "—", "rec_desc": "", "error": msg})
        return render_template("index.html", active_tab="recommender", recommendation=msg)

    try:
        mrt_dist    = float(request.form.get("mrt_distance") or 0)
        hawker_dist = float(request.form.get("hawker_distance") or 0)
        hdb_age     = float(request.form.get("hdb_age") or 0)
        max_floor   = float(request.form.get("max_floor_lvl") or 1)

        total_distance  = mrt_dist + hawker_dist
        age_floor_ratio = hdb_age / max(max_floor, 1)

        features = np.array([[hawker_dist, max_floor, mrt_dist,
                               hdb_age, total_distance, age_floor_ratio]])
        features_scaled = _clf_scaler.transform(features)

        pred_idx  = _rf_clf.predict(features_scaled)[0]
        pred_town = _TOWN_CLASSES[pred_idx]
        result    = f"Recommended Town: {pred_town}"
    except Exception as e:
        pred_town = None
        result = f"Error: {e}"

    rec_desc = _TOWN_DESCRIPTIONS.get(pred_town, "") if pred_town else ""
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


if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, use_reloader=debug)
