from flask import Flask, render_template, request

app = Flask(__name__)


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
    # TODO: Replace stub with real classification/recommender model
    # Inputs available via request.form:
    #   budget_min, budget_max, preferred_town, flat_type
    stub_result = "Recommender coming soon"
    return render_template(
        "index.html",
        active_tab="recommender",
        recommendation=stub_result,
    )


if __name__ == "__main__":
    import os
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", use_reloader=False)
