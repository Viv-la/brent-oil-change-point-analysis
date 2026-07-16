from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_csv(filename: str) -> pd.DataFrame:
    file_path = PROCESSED_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {file_path}"
        )

    return pd.read_csv(file_path)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Brent Oil Change Point Analysis API",
        "status": "running",
        "endpoints": {
            "prices": "/api/prices",
            "events": "/api/events",
            "change_point": "/api/change-point",
            "summary": "/api/summary"
        }
    })


@app.route("/api/prices", methods=["GET"])
def get_prices():
    prices_df = load_csv("monthly_prices.csv")
    prices_df["Date"] = pd.to_datetime(
        prices_df["Date"],
        errors="coerce"
    )

    start_date = request.args.get("start")
    end_date = request.args.get("end")

    if start_date:
        prices_df = prices_df[
            prices_df["Date"] >= pd.to_datetime(start_date)
        ]

    if end_date:
        prices_df = prices_df[
            prices_df["Date"] <= pd.to_datetime(end_date)
        ]

    prices_df["Date"] = prices_df["Date"].dt.strftime(
        "%Y-%m-%d"
    )

    return jsonify(prices_df.to_dict(orient="records"))


@app.route("/api/events", methods=["GET"])
def get_events():
    events_df = load_csv("event_analysis.csv")
    events_df["Date"] = pd.to_datetime(
        events_df["Date"],
        errors="coerce"
    )

    category = request.args.get("category")

    if category:
        events_df = events_df[
            events_df["Category"].str.lower()
            == category.lower()
        ]

    events_df["Date"] = events_df["Date"].dt.strftime(
        "%Y-%m-%d"
    )

    events_df = events_df.where(
        pd.notnull(events_df),
        None
    )

    return jsonify(events_df.to_dict(orient="records"))


@app.route("/api/change-point", methods=["GET"])
def get_change_point():
    result_df = load_csv("change_point_results.csv")

    result_df = result_df.where(
        pd.notnull(result_df),
        None
    )

    return jsonify(result_df.to_dict(orient="records")[0])


@app.route("/api/summary", methods=["GET"])
def get_summary():
    prices_df = load_csv("monthly_prices.csv")
    events_df = load_csv("event_analysis.csv")

    summary = {
        "average_price": round(
            prices_df["Price"].mean(),
            2
        ),
        "minimum_price": round(
            prices_df["Price"].min(),
            2
        ),
        "maximum_price": round(
            prices_df["Price"].max(),
            2
        ),
        "total_observations": int(len(prices_df)),
        "total_events": int(len(events_df)),
        "average_event_impact": round(
            events_df["Percentage_Change"].mean(),
            2
        )
    }

    return jsonify(summary)


@app.errorhandler(FileNotFoundError)
def handle_missing_file(error):
    return jsonify({
        "error": str(error)
    }), 404


@app.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({
        "error": str(error)
    }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )