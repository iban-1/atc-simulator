import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchProgression } from "../services/api.js";

const CHART_COLORS = {
  score: "#22d38a",
  handled: "#60a5fa",
  safe: "#22d38a",
  conflicts: "#fbbf24",
  violations: "#f87171",
  delay: "#a78bfa",
};

function ChartCard({ title, children }) {
  return (
    <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">{title}</h3>
      <div style={{ width: "100%", height: 220 }}>{children}</div>
    </div>
  );
}

function buildByScenario(history) {
  const grouped = new Map();
  for (const entry of history) {
    const bucket = grouped.get(entry.scenario_name) ?? { scenario: entry.scenario_name, totalScore: 0, games: 0 };
    bucket.totalScore += entry.score;
    bucket.games += 1;
    grouped.set(entry.scenario_name, bucket);
  }
  return Array.from(grouped.values()).map((b) => ({
    scenario: b.scenario,
    averageScore: Math.round(b.totalScore / b.games),
    games: b.games,
  }));
}

export default function AnalyticsPage({ onBack }) {
  const [progression, setProgression] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetchProgression()
      .then((data) => {
        if (!cancelled) setProgression(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const history = progression?.history ?? [];
  const chartData = history.map((entry, i) => ({
    game: i + 1,
    score: entry.score,
    handled: entry.aircraft_handled,
    safe: entry.aircraft_safe,
    conflicts: entry.conflicts_detected,
    violations: entry.separation_violations,
    delay: Number(entry.average_delay_s.toFixed(1)),
    scenario: entry.scenario_name,
  }));
  const byScenario = buildByScenario(history);

  return (
    <div className="h-screen overflow-y-auto bg-black px-6 py-8 text-zinc-200">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-emerald-400">ANALYTICS</h1>
            <p className="text-xs uppercase tracking-widest text-zinc-500">performance history &middot; fictional simulation data</p>
          </div>
          <button
            onClick={onBack}
            className="rounded bg-zinc-800 px-4 py-2 text-sm font-semibold text-zinc-200 hover:bg-zinc-700"
          >
            Back to Scenarios
          </button>
        </div>

        {error && <div className="mb-4 rounded bg-red-950/50 px-3 py-2 text-xs text-red-300">{error}</div>}

        {progression && history.length === 0 && (
          <div className="rounded border border-zinc-800 bg-zinc-950 p-8 text-center text-sm text-zinc-500">
            Play a scenario to see analytics here.
          </div>
        )}

        {history.length > 0 && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartCard title="Score History">
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="game" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", fontSize: 12 }} />
                  <Line type="monotone" dataKey="score" stroke={CHART_COLORS.score} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Aircraft Handled">
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="game" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="handled" name="Handled" fill={CHART_COLORS.handled} />
                  <Bar dataKey="safe" name="Safe" fill={CHART_COLORS.safe} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Conflict History">
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="game" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="conflicts" name="Conflicts" stroke={CHART_COLORS.conflicts} strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="violations" name="Violations" stroke={CHART_COLORS.violations} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Average Delay (seconds)">
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="game" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", fontSize: 12 }} />
                  <Line type="monotone" dataKey="delay" stroke={CHART_COLORS.delay} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Performance by Scenario (avg. score)">
              <ResponsiveContainer>
                <BarChart data={byScenario} layout="vertical" margin={{ left: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis type="number" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="scenario" stroke="#71717a" tick={{ fontSize: 11 }} width={110} />
                  <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", fontSize: 12 }} />
                  <Bar dataKey="averageScore" fill={CHART_COLORS.score} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>
        )}
      </div>
    </div>
  );
}
