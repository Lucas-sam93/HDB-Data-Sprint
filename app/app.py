import json
import numpy as np
from pathlib import Path

from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load classification model artefacts at startup
# ---------------------------------------------------------------------------
_MODEL_DIR = Path(__file__).parent / "models"
try:
    _rf_clf      = joblib.load(_MODEL_DIR / "rf_classifier.joblib")
    _clf_scaler  = joblib.load(_MODEL_DIR / "scaler_classifier.joblib")
    with open(_MODEL_DIR / "town_classes.json") as _f:
        _TOWN_CLASSES = json.load(_f)
    _clf_ready = True
except FileNotFoundError:
    _clf_ready = False  # Models not yet exported from notebook


@app.route("/")
def index():
    return render_template("index.html", active_tab="estimator")


@app.route("/predict", methods=["POST"])
def predict():
    # TODO: Replace stub with real XGBoost model inference
    # Inputs available via request.form:
    #   flat_type, town, flat_model, floor_area_sqm, storey,
    #   hdb_age, mrt_distance, mall_distance
    stub_price = "$450,000"
    stub_note = "Demo mode — model not yet connected"
    return render_template(
        "index.html",
        active_tab="estimator",
        price=stub_price,
        price_note=stub_note,
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
