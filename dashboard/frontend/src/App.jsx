import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";

const API_BASE = "http://127.0.0.1:5000/api";

function formatMoney(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `$${number.toFixed(2)}` : "N/A";
}

function App() {
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [changePoint, setChangePoint] = useState(null);

  const [category, setCategory] = useState("All");
  const [startDate, setStartDate] = useState("1987-05-01");
  const [endDate, setEndDate] = useState("2022-09-30");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [
          pricesResponse,
          eventsResponse,
          summaryResponse,
          changePointResponse,
        ] = await Promise.all([
          axios.get(`${API_BASE}/prices`),
          axios.get(`${API_BASE}/events`),
          axios.get(`${API_BASE}/summary`),
          axios.get(`${API_BASE}/change-point`),
        ]);

       const pricesData = Array.isArray(pricesResponse.data)
  ? pricesResponse.data
  : pricesResponse.data?.data ||
    pricesResponse.data?.prices ||
    [];

const eventsData = Array.isArray(eventsResponse.data)
  ? eventsResponse.data
  : eventsResponse.data?.data ||
    eventsResponse.data?.events ||
    [];

setPrices(pricesData);
setEvents(eventsData);
setSummary(summaryResponse.data || {});
setChangePoint(changePointResponse.data || {});
      } catch (requestError) {
        console.error(requestError);
        setError(
          "The dashboard could not load data. Confirm that the Flask API is running on http://127.0.0.1:5000."
        );
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const categories = useMemo(() => {
  if (!Array.isArray(events)) {
    return ["All"];
  }

  const uniqueCategories = [
    ...new Set(
      events
        .map((event) => event?.Category)
        .filter(Boolean)
    ),
  ];

  return ["All", ...uniqueCategories];
}, [events]);

  const filteredPrices = useMemo(() => {
    return prices.filter(
      (row) => row.Date >= startDate && row.Date <= endDate
    );
  }, [prices, startDate, endDate]);

  const filteredEvents = useMemo(() => {
  if (!Array.isArray(events)) {
    return [];
  }

  return events.filter((event) => {
    const categoryMatch =
      category === "All" || event?.Category === category;

    const dateMatch =
      event?.Date >= startDate &&
      event?.Date <= endDate;

    return categoryMatch && dateMatch;
  });
}, [events, category, startDate, endDate]);

  const largestImpacts = useMemo(() => {
    return [...filteredEvents]
      .filter(
        (event) =>
          event.Percentage_Change !== null &&
          event.Percentage_Change !== undefined
      )
      .sort(
        (a, b) =>
          Math.abs(Number(b.Percentage_Change)) -
          Math.abs(Number(a.Percentage_Change))
      )
      .slice(0, 8);
  }, [filteredEvents]);

  if (loading) {
    return <div className="status-message">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="status-message error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <header className="hero">
        <p className="eyebrow">Birhan Energies Analytics</p>
        <h1>Brent Oil Change Point Dashboard</h1>
        <p className="hero-copy">
          Explore structural shifts in Brent crude oil prices and their
          association with geopolitical, economic, and OPEC-related events.
        </p>
      </header>

      <section className="filters">
        <div className="filter-control">
          <label htmlFor="startDate">Start date</label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </div>

        <div className="filter-control">
          <label htmlFor="endDate">End date</label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </div>

        <div className="filter-control">
          <label htmlFor="category">Event category</label>
          <select
            id="category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            {categories.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
      </section>

      <section className="metrics">
        <article className="metric-card">
          <span>Average Price</span>
          <strong>{formatMoney(summary?.average_price)}</strong>
        </article>

        <article className="metric-card">
          <span>Maximum Price</span>
          <strong>{formatMoney(summary?.maximum_price)}</strong>
        </article>

        <article className="metric-card">
          <span>Detected Change Point</span>
          <strong>{changePoint?.change_point_date || "N/A"}</strong>
        </article>

        <article className="metric-card">
          <span>Estimated Price Shift</span>
          <strong>
            {Number(changePoint?.percentage_change || 0).toFixed(2)}%
          </strong>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Historical Brent Price Trend</h2>
          <p>
            Monthly average Brent prices with the Bayesian change point
            highlighted.
          </p>
        </div>

        <div className="chart chart-large">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={filteredPrices}
              margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="Date" minTickGap={45} />
              <YAxis />
              <Tooltip
                formatter={(value) => [formatMoney(value), "Price"]}
              />
              <Line
                type="monotone"
                dataKey="Price"
                dot={false}
                strokeWidth={2}
              />

              {changePoint?.change_point_date && (
                <ReferenceLine
                  x={changePoint.change_point_date}
                  strokeDasharray="6 6"
                  label="Detected Change Point"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="split-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Largest Event Impacts</h2>
            <p>
              Average price change three months before and after each event.
            </p>
          </div>

          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={largestImpacts}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 50, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis
                  type="category"
                  dataKey="Event"
                  width={190}
                />
                <Tooltip
                  formatter={(value) => [
                    `${Number(value).toFixed(2)}%`,
                    "Price Change",
                  ]}
                />
                <Bar dataKey="Percentage_Change" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h2>Change Point Summary</h2>
            <p>Posterior estimates from the Bayesian model.</p>
          </div>

          <div className="summary-list">
            <div>
              <span>Mean before change</span>
              <strong>{formatMoney(changePoint?.mean_before)}</strong>
            </div>

            <div>
              <span>Mean after change</span>
              <strong>{formatMoney(changePoint?.mean_after)}</strong>
            </div>

            <div>
              <span>Absolute change</span>
              <strong>{formatMoney(changePoint?.absolute_change)}</strong>
            </div>

            <div>
              <span>Probability of increase</span>
              <strong>
                {(
                  Number(changePoint?.probability_increase || 0) * 100
                ).toFixed(2)}
                %
              </strong>
            </div>

            <div>
              <span>Probability of decrease</span>
              <strong>
                {(
                  Number(changePoint?.probability_decrease || 0) * 100
                ).toFixed(2)}
                %
              </strong>
            </div>
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Event Drill-Down</h2>
          <p>
            Filtered event records showing expected and observed impacts.
          </p>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Event</th>
                <th>Category</th>
                <th>Expected Impact</th>
                <th>Observed Direction</th>
                <th>Price Change</th>
              </tr>
            </thead>

            <tbody>
              {filteredEvents.map((event) => (
                <tr key={`${event.Date}-${event.Event}`}>
                  <td>{event.Date}</td>
                  <td>{event.Event}</td>
                  <td>{event.Category}</td>
                  <td>{event.Expected_Impact}</td>
                  <td>{event.Observed_Direction}</td>
                  <td>
                    {event.Percentage_Change === null
                      ? "N/A"
                      : `${Number(
                          event.Percentage_Change
                        ).toFixed(2)}%`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        Statistical association does not establish causation. Multiple market
        forces may overlap around each event.
      </footer>
    </div>
  );
}

export default App;