const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchScenarios() {
  const res = await fetch(`${API_URL}/api/scenarios`);
  if (!res.ok) throw new Error(`Failed to fetch scenarios: ${res.status}`);
  return res.json();
}

export async function startScenario(scenarioId) {
  const res = await fetch(`${API_URL}/api/scenarios/${scenarioId}/start`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to start scenario: ${res.status}`);
  return res.json();
}

export async function fetchProgression() {
  const res = await fetch(`${API_URL}/api/progression`);
  if (!res.ok) throw new Error(`Failed to fetch progression: ${res.status}`);
  return res.json();
}
