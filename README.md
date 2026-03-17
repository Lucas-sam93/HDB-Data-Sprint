# HDB Resale Price Predictor

Sprint project for a data analytics bootcamp. We are data analysts at **WOW! Real Estate**, a Singapore property agency. The goal is to analyse the HDB resale market and build ML models to predict resale prices and recommend towns.

## Features

- **Price Estimator** — XGBoost regression model predicting resale price with a ±10% confidence range
- **Town Recommender** — Random Forest classifier recommending the best Singapore town based on lifestyle preferences
- **Web App** — Flask UI with light/dark mode, pill selectors, town typeahead, and distance sliders

## Dataset

`data.csv` — HDB resale transaction data (270,620 rows, 76 columns). Tracked via Git LFS.

## Setup

```bash
pip install -r requirements.txt
```

Models must be exported from the notebooks before running the app:

1. Run `notebooks/Regression_Models_Comparison.ipynb` — exports `app/models/xgb_regressor.joblib`
2. Run `notebooks/Classification_Models_Comparison.ipynb` — exports `app/models/rf_classifier.joblib`

## Running the App

Double-click `run.bat` or run from terminal:

```bash
python app/app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure

```
├── app/
│   ├── app.py                  # Flask routes
│   ├── models/                 # Exported model artefacts (gitignored .joblib)
│   ├── static/style.css
│   └── templates/index.html
├── notebooks/
│   ├── EDA_sprint.ipynb
│   ├── Regression_Models_Comparison.ipynb
│   └── Classification_Models_Comparison.ipynb
├── data.csv                    # Source data (Git LFS)
└── requirements.txt
```
