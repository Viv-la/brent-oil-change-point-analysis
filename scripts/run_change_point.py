from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
import arviz as az


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "BrentOilPrices.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42


# ------------------------------------------------------------
# Load and prepare data
# ------------------------------------------------------------

print("Loading Brent oil data...")

df = pd.read_csv(DATA_PATH)

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%b-%y",
    errors="coerce",
)

df["Price"] = pd.to_numeric(
    df["Price"],
    errors="coerce",
)

df = (
    df.dropna(subset=["Date", "Price"])
    .drop_duplicates(subset=["Date"])
    .sort_values("Date")
    .reset_index(drop=True)
)

monthly_df = (
    df.set_index("Date")["Price"]
    .resample("MS")
    .mean()
    .dropna()
    .reset_index()
)

monthly_df.columns = ["Date", "Price"]

prices = monthly_df["Price"].to_numpy(dtype="float64")
time_index = np.arange(len(prices))

print(f"Monthly observations: {len(monthly_df)}")
print(
    f"Date range: {monthly_df['Date'].min().date()} "
    f"to {monthly_df['Date'].max().date()}"
)


# ------------------------------------------------------------
# Bayesian change-point model
# ------------------------------------------------------------

print("\nBuilding Bayesian change-point model...")

with pm.Model() as change_point_model:

    tau = pm.DiscreteUniform(
        "tau",
        lower=1,
        upper=len(prices) - 2,
    )

    mu_before = pm.Normal(
        "mu_before",
        mu=prices.mean(),
        sigma=prices.std() * 2,
    )

    mu_after = pm.Normal(
        "mu_after",
        mu=prices.mean(),
        sigma=prices.std() * 2,
    )

    sigma = pm.HalfNormal(
        "sigma",
        sigma=prices.std(),
    )

    expected_mean = pm.math.switch(
        time_index < tau,
        mu_before,
        mu_after,
    )

    pm.Normal(
        "observed_prices",
        mu=expected_mean,
        sigma=sigma,
        observed=prices,
    )

    step_continuous = pm.NUTS(
        vars=[mu_before, mu_after, sigma],
        target_accept=0.90,
    )

    step_discrete = pm.Metropolis(
        vars=[tau],
    )

    print("Running MCMC sampling...")

    trace = pm.sample(
        draws=1200,
        tune=800,
        chains=2,
        cores=1,
        step=[step_continuous, step_discrete],
        random_seed=RANDOM_SEED,
        return_inferencedata=True,
        progressbar=True,
    )


# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

summary = az.summary(
    trace,
    var_names=["tau", "mu_before", "mu_after", "sigma"],
    round_to=3,
)

summary.to_csv(
    PROCESSED_DIR / "bayesian_model_summary.csv"
)

print("\nBayesian model summary:")
print(summary)


# ------------------------------------------------------------
# Extract posterior results
# ------------------------------------------------------------

tau_samples = trace.posterior["tau"].values.flatten()
mu_before_samples = trace.posterior["mu_before"].values.flatten()
mu_after_samples = trace.posterior["mu_after"].values.flatten()

tau_mode = int(pd.Series(tau_samples).mode().iloc[0])
change_date = monthly_df.loc[tau_mode, "Date"]

mu_before_mean = float(mu_before_samples.mean())
mu_after_mean = float(mu_after_samples.mean())

absolute_change = mu_after_mean - mu_before_mean
percentage_change = (
    absolute_change / mu_before_mean
) * 100

probability_increase = float(
    np.mean(mu_after_samples > mu_before_samples)
)

probability_decrease = float(
    np.mean(mu_after_samples < mu_before_samples)
)

before_interval = np.quantile(
    mu_before_samples,
    [0.025, 0.975],
)

after_interval = np.quantile(
    mu_after_samples,
    [0.025, 0.975],
)


# ------------------------------------------------------------
# Save model results
# ------------------------------------------------------------

results_df = pd.DataFrame(
    {
        "change_point_index": [tau_mode],
        "change_point_date": [
            change_date.strftime("%Y-%m-%d")
        ],
        "mean_before": [mu_before_mean],
        "mean_after": [mu_after_mean],
        "absolute_change": [absolute_change],
        "percentage_change": [percentage_change],
        "probability_increase": [probability_increase],
        "probability_decrease": [probability_decrease],
        "before_lower_95": [before_interval[0]],
        "before_upper_95": [before_interval[1]],
        "after_lower_95": [after_interval[0]],
        "after_upper_95": [after_interval[1]],
    }
)

results_df.to_csv(
    PROCESSED_DIR / "change_point_results.csv",
    index=False,
)

monthly_df.to_csv(
    PROCESSED_DIR / "monthly_prices.csv",
    index=False,
)


# ------------------------------------------------------------
# Generate required figures
# ------------------------------------------------------------

print("\nSaving figures...")

# 1. Trace plot
az.plot_trace(
    trace,
    var_names=["tau", "mu_before", "mu_after", "sigma"],
)

plt.savefig(
    FIGURES_DIR / "trace_plot.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close("all")


# 2. Posterior distribution of tau
# 2. Posterior distribution of tau
plt.figure(figsize=(10, 6))

plt.hist(
    tau_samples,
    bins=35,
    density=True,
    alpha=0.8
)

plt.axvline(
    tau_mode,
    linestyle="--",
    linewidth=2,
    label=f"Most probable index: {tau_mode}"
)

plt.title("Posterior Distribution of the Change Point")
plt.xlabel("Monthly Observation Index")
plt.ylabel("Posterior Density")
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "tau_posterior.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# 3. Before and after posterior distributions
# 3. Posterior distributions of means before and after
plt.figure(figsize=(11, 6))

plt.hist(
    mu_before_samples,
    bins=35,
    density=True,
    alpha=0.65,
    label="Mean Before Change"
)

plt.hist(
    mu_after_samples,
    bins=35,
    density=True,
    alpha=0.65,
    label="Mean After Change"
)

plt.axvline(
    mu_before_mean,
    linestyle="--",
    linewidth=2
)

plt.axvline(
    mu_after_mean,
    linestyle="--",
    linewidth=2
)

plt.title("Posterior Distributions of Mean Brent Prices")
plt.xlabel("Price — USD per Barrel")
plt.ylabel("Posterior Density")
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "mean_posterior.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# 4. Change point displayed on time series
plt.figure(figsize=(15, 6))

plt.plot(
    monthly_df["Date"],
    monthly_df["Price"],
    linewidth=1.2,
    label="Monthly Brent Price",
)

plt.axvline(
    change_date,
    linestyle="--",
    linewidth=2.5,
    label=f"Change Point: {change_date:%Y-%m}",
)

plt.axhline(
    mu_before_mean,
    linestyle=":",
    linewidth=2,
    label=f"Mean Before: ${mu_before_mean:.2f}",
)

plt.axhline(
    mu_after_mean,
    linestyle="-.",
    linewidth=2,
    label=f"Mean After: ${mu_after_mean:.2f}",
)

plt.title(
    "Bayesian Change Point in Brent Oil Prices"
)

plt.xlabel("Date")
plt.ylabel("Price — USD per barrel")
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "change_point.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# Print final results
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("FINAL BAYESIAN CHANGE-POINT RESULTS")
print("=" * 65)

print(
    f"Detected change point: "
    f"{change_date.strftime('%Y-%m-%d')}"
)

print(
    f"Estimated mean before change: "
    f"${mu_before_mean:.2f}"
)

print(
    f"Estimated mean after change: "
    f"${mu_after_mean:.2f}"
)

print(
    f"Absolute price shift: "
    f"${absolute_change:.2f}"
)

print(
    f"Percentage price shift: "
    f"{percentage_change:.2f}%"
)

print(
    f"Probability of increase: "
    f"{probability_increase:.2%}"
)

print(
    f"Probability of decrease: "
    f"{probability_decrease:.2%}"
)

print(
    f"95% interval before: "
    f"${before_interval[0]:.2f} "
    f"to ${before_interval[1]:.2f}"
)

print(
    f"95% interval after: "
    f"${after_interval[0]:.2f} "
    f"to ${after_interval[1]:.2f}"
)

print("=" * 65)

print("\nFiles created successfully:")

print(
    PROCESSED_DIR / "change_point_results.csv"
)

print(
    PROCESSED_DIR / "bayesian_model_summary.csv"
)

print(
    FIGURES_DIR / "trace_plot.png"
)

print(
    FIGURES_DIR / "tau_posterior.png"
)

print(
    FIGURES_DIR / "mean_posterior.png"
)

print(
    FIGURES_DIR / "change_point.png"
)