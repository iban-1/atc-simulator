import { useState } from "react";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import GamePage from "./pages/GamePage.jsx";
import ScenarioSelectPage from "./pages/ScenarioSelectPage.jsx";

export default function RootApp() {
  const [view, setView] = useState("select");

  if (view === "game") {
    return <GamePage onExitToSelect={() => setView("select")} />;
  }
  if (view === "analytics") {
    return <AnalyticsPage onBack={() => setView("select")} />;
  }
  return <ScenarioSelectPage onScenarioStarted={() => setView("game")} onViewAnalytics={() => setView("analytics")} />;
}
