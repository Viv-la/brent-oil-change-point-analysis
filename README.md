# Brent Oil Price Change Point Analysis

## Project Overview

This project investigates structural changes in Brent crude oil prices using Bayesian Change Point Analysis and evaluates the impact of major geopolitical, economic, and health-related events on global oil markets.

The project was completed as part of the 10 Academy Artificial Intelligence Mastery Program (Week 10 Challenge) for Birhan Energies.

---

# Business Problem

Brent crude oil prices are highly sensitive to geopolitical conflicts, economic crises, OPEC production decisions, and global health emergencies. Understanding when significant structural shifts occur enables investors, policymakers, and energy companies to make more informed strategic decisions.

This project aims to identify statistically significant change points in historical Brent oil prices and associate them with major historical events.

---

# Objectives

- Perform exploratory analysis of Brent crude oil prices
- Detect structural breaks using Bayesian Change Point Analysis
- Associate detected changes with major historical events
- Quantify the impact of important geopolitical and economic events
- Develop a dashboard for interactive visualization of results

---

# Repository Structure

```
brent-oil-change-point-analysis/

├── dashboard/
│   ├── backend/
│   └── frontend/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_ChangePoint.ipynb
│   └── 03_EventAnalysis.ipynb
│
├── reports/
│   ├── figures/
│   ├── Interim_Report.md
│   └── Final_Report.md
│
├── scripts/
│
├── src/
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# Methodology

## 1. Data Preparation

- Historical Brent crude oil prices
- Monthly aggregation
- Missing value handling
- Time-series preparation

---

## 2. Exploratory Data Analysis

The exploratory analysis examined:

- Historical price trends
- Long-term volatility
- Monthly average prices
- Time-series characteristics

---

## 3. Bayesian Change Point Analysis

A Bayesian Change Point Model was implemented using PyMC.

Model parameters:

- Discrete change point (τ)
- Mean price before change
- Mean price after change
- Observation variance

Posterior inference was obtained using Markov Chain Monte Carlo (MCMC) sampling.

---

## 4. Event Impact Analysis

Major geopolitical, economic and OPEC events were analysed by comparing the average Brent oil prices during the three months before and after each event.

---

# Dashboard

The project includes a Flask backend and a React frontend.

### API Endpoints

- `/api/prices`
- `/api/events`
- `/api/change-point`
- `/api/summary`

---

# Key Results

## Bayesian Model

Detected Change Point

**1 March 2005**

Estimated Mean Before

**$21.47 per barrel**

Estimated Mean After

**$76.00 per barrel**

Absolute Increase

**$54.53**

Percentage Increase

**254.04%**

Posterior Probability of Increase

**100%**

95% Credible Interval (Before)

$18.91 – $23.97

95% Credible Interval (After)

$73.23 – $78.62

---

# Largest Event Impacts

| Event | Percentage Change |
|---------|------------------|
| Iraq invades Kuwait | +74.94% |
| COVID-19 Pandemic | -61.11% |
| Saudi-Russia Oil Price War | -61.11% |
| Global Financial Crisis | -52.22% |
| OPEC Production Decision | -36.28% |

---

# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- PyMC
- ArviZ
- Flask
- React
- Vite

---

# Installation

Clone repository

```bash
git clone https://github.com/Viv-la/brent-oil-change-point-analysis.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run Bayesian analysis

```bash
py scripts/run_change_point.py
```

Run Event Analysis

```bash
py scripts/run_event_analysis.py
```

Start Flask API

```bash
py dashboard/backend/app.py
```

Start React Dashboard

```bash
cd dashboard/frontend

npm install

npm run dev
```

---

# Key Findings

The Bayesian model identified a statistically significant structural shift around March 2005, indicating a transition from a prolonged low-price regime to a sustained high-price regime.

The analysis also demonstrated that major geopolitical conflicts, global economic crises, and OPEC production decisions produced substantial short-term impacts on Brent oil prices.

The Iraq invasion of Kuwait generated the largest positive price increase (+74.94%), while both the COVID-19 pandemic and the Saudi-Russia oil price war produced the largest negative impacts (-61.11%).

---

# Limitations

- Single change-point assumption
- Historical events may overlap
- External macroeconomic variables were not explicitly modelled
- Correlation does not necessarily imply causation

---

# Future Work

- Multiple change-point Bayesian models
- Hidden Markov Models
- Macroeconomic variable integration
- Real-time dashboard deployment
- Forecasting future structural changes

---

# Author

**Frida N.**

10 Academy Artificial Intelligence Mastery Program