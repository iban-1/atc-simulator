import AircraftList from "./components/AircraftList.jsx";
import AlertsPanel from "./components/AlertsPanel.jsx";
import BottomBar from "./components/BottomBar.jsx";
import CommandPanel from "./components/CommandPanel.jsx";
import CommsPanel from "./components/CommsPanel.jsx";
import GameOverOverlay from "./components/GameOverOverlay.jsx";
import LandingSequencePanel from "./components/LandingSequencePanel.jsx";
import RadarCanvas from "./components/RadarCanvas.jsx";
import SectorPanel from "./components/SectorPanel.jsx";
import SelectedAircraftInfo from "./components/SelectedAircraftInfo.jsx";
import TopBar from "./components/TopBar.jsx";

export default function App({ onExitToSelect }) {
  return (
    <div className="flex h-screen flex-col bg-black text-zinc-200">
      <TopBar />
      <div className="relative flex flex-1 overflow-hidden">
        <aside className="w-64 shrink-0 overflow-hidden">
          <AircraftList />
        </aside>

        <main className="relative flex-1">
          <RadarCanvas />
          <GameOverOverlay onExitToSelect={onExitToSelect} />
        </main>

        <aside className="flex w-80 shrink-0 flex-col overflow-hidden border-l border-zinc-800 bg-zinc-950">
          <div className="border-b border-zinc-800">
            <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Selected Aircraft
            </div>
            <SelectedAircraftInfo />
          </div>
          <div className="border-b border-zinc-800">
            <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Controller Commands
            </div>
            <CommandPanel />
          </div>
          <div className="min-h-0 flex-1 overflow-hidden border-b border-zinc-800">
            <CommsPanel />
          </div>
          <AlertsPanel />
          <SectorPanel />
          <LandingSequencePanel />
        </aside>
      </div>
      <BottomBar />
    </div>
  );
}
