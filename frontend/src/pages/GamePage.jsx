import App from "../App.jsx";
import { SimulationProvider } from "../hooks/useSimulation.jsx";

export default function GamePage({ onExitToSelect }) {
  return (
    <SimulationProvider>
      <App onExitToSelect={onExitToSelect} />
    </SimulationProvider>
  );
}
