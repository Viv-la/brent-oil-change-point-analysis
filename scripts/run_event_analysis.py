from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENTS_PATH = (
    PROJECT_ROOT / "data" / "raw" / "oil_events.csv"
)

PRICES_PATH = (
    PROJECT_ROOT / "data" / "processed" / "monthly_prices.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


events_df = pd.read_csv(EVENTS_PATH)
prices_df = pd.read_csv(PRICES_PATH)

events_df["Date"] = pd.to_datetime(
    events_df["Date"],
    errors="coerce"
)

prices_df["Date"] = pd.to_datetime(
    prices_df["Date"],
    errors="coerce"
)

events_df = (
    events_df.dropna(subset=["Date"])
    .sort_values("Date")
    .reset_index(drop=True)
)

prices_df = (
    prices_df.dropna(subset=["Date", "Price"])
    .sort_values("Date")
    .reset_index(drop=True)
)


def calculate_event_impact(
    event_date,
    months_before=3,
    months_after=3,
):
    event_date = pd.Timestamp(event_date)

    before_start = (
        event_date - pd.DateOffset(months=months_before)
    )

    after_end = (
        event_date + pd.DateOffset(months=months_after)
    )

    before_prices = prices_df[
        (prices_df["Date"] >= before_start)
        & (prices_df["Date"] < event_date)
    ]["Price"]

    after_prices = prices_df[
        (prices_df["Date"] >= event_date)
        & (prices_df["Date"] <= after_end)
    ]["Price"]

    if before_prices.empty or after_prices.empty:
        return pd.Series(
            {
                "Average_Before": np.nan,
                "Average_After": np.nan,
                "Absolute_Change": np.nan,
                "Percentage_Change": np.nan,
            }
        )

    average_before = before_prices.mean()
    average_after = after_prices.mean()

    absolute_change = average_after - average_before

    percentage_change = (
        absolute_change / average_before
    ) * 100

    return pd.Series(
        {
            "Average_Before": average_before,
            "Average_After": average_after,
            "Absolute_Change": absolute_change,
            "Percentage_Change": percentage_change,
        }
    )


event_impacts = events_df.apply(
    lambda row: calculate_event_impact(row["Date"]),
    axis=1,
)

event_analysis_df = pd.concat(
    [events_df, event_impacts],
    axis=1,
)

event_analysis_df["Observed_Direction"] = np.where(
    event_analysis_df["Percentage_Change"] >= 0,
    "Increase",
    "Decrease",
)

event_analysis_df["Absolute_Percentage_Change"] = (
    event_analysis_df["Percentage_Change"].abs()
)

event_analysis_df = event_analysis_df.sort_values(
    "Absolute_Percentage_Change",
    ascending=False,
)

event_analysis_df.to_csv(
    PROCESSED_DIR / "event_analysis.csv",
    index=False,
)


top_events = event_analysis_df.head(10).copy()
plot_df = top_events.sort_values("Percentage_Change")


plt.figure(figsize=(12, 8))

plt.barh(
    plot_df["Event"],
    plot_df["Percentage_Change"],
)

plt.axvline(
    0,
    linewidth=1,
)

plt.title(
    "Largest Brent Oil Price Changes Around Major Events"
)

plt.xlabel(
    "Average Price Change: "
    "Three Months Before vs. Three Months After (%)"
)

plt.ylabel("Event")
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "event_impacts.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


plt.figure(figsize=(16, 7))

plt.plot(
    prices_df["Date"],
    prices_df["Price"],
    linewidth=1.2,
    label="Monthly Brent Price",
)

for _, event in events_df.iterrows():
    plt.axvline(
        event["Date"],
        linestyle="--",
        linewidth=0.7,
        alpha=0.35,
    )

plt.title(
    "Brent Oil Prices and Major Geopolitical, "
    "Economic and OPEC Events"
)

plt.xlabel("Date")
plt.ylabel("Price — USD per Barrel")
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "events_on_price_series.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


print("\nTOP EVENT IMPACTS")
print("=" * 90)

print(
    top_events[
        [
            "Date",
            "Event",
            "Category",
            "Average_Before",
            "Average_After",
            "Percentage_Change",
            "Observed_Direction",
        ]
    ].round(2).to_string(index=False)
)

print("\nFiles created successfully:")

print(PROCESSED_DIR / "event_analysis.csv")
print(FIGURES_DIR / "event_impacts.png")
print(FIGURES_DIR / "events_on_price_series.png")