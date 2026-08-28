import { createContext, useCallback, useContext, useMemo, useReducer } from "react";
import { useWebSocket } from "./useWebSocket.js";

const SimulationContext = createContext(null);

const MAX_COMMS_LOG = 100;
const MAX_TRAIL_POINTS = 20;

const initialState = {
  scenario: null,
  waypoints: [],
  routes: [],
  airspaceBounds: null,
  stateUpdate: null,
  commsLog: [],
  gameOverResult: null,
  selectedAircraftId: null,
  errorMessage: null,
  trails: {},
  view: { centerX: 0, centerY: 0, pixelsPerNm: 4 },
  toggles: { labels: true, trails: true, routes: true, sectors: true, waypoints: true },
};

function updateTrails(trails, aircraftList) {
  const next = {};
  for (const ac of aircraftList) {
    const prev = trails[ac.id] || [];
    next[ac.id] = [...prev, { x: ac.x, y: ac.y }].slice(-MAX_TRAIL_POINTS);
  }
  return next;
}

function reducer(state, action) {
  switch (action.type) {
    case "FULL_SNAPSHOT": {
      const { scenario, waypoints, routes, airspace_bounds, state_update } = action.payload;
      return {
        ...state,
        scenario,
        waypoints,
        routes,
        airspaceBounds: airspace_bounds,
        stateUpdate: state_update,
        gameOverResult: null,
        commsLog: [],
        trails: updateTrails({}, state_update.aircraft),
      };
    }
    case "STATE_UPDATE": {
      const stillSelected =
        state.selectedAircraftId && action.payload.aircraft.some((a) => a.id === state.selectedAircraftId);
      return {
        ...state,
        stateUpdate: action.payload,
        trails: updateTrails(state.trails, action.payload.aircraft),
        selectedAircraftId: stillSelected ? state.selectedAircraftId : null,
      };
    }
    case "COMMS_MESSAGE":
      return { ...state, commsLog: [...state.commsLog, action.payload].slice(-MAX_COMMS_LOG) };
    case "GAME_OVER":
      return { ...state, gameOverResult: action.payload };
    case "ERROR":
      return { ...state, errorMessage: action.payload };
    case "CLEAR_ERROR":
      return { ...state, errorMessage: null };
    case "SELECT_AIRCRAFT":
      return { ...state, selectedAircraftId: action.payload };
    case "SET_VIEW":
      return { ...state, view: { ...state.view, ...action.payload } };
    case "TOGGLE":
      return { ...state, toggles: { ...state.toggles, [action.payload]: !state.toggles[action.payload] } };
    case "RESET_FOR_RESTART":
      return { ...state, commsLog: [], gameOverResult: null, trails: {}, selectedAircraftId: null };
    default:
      return state;
  }
}

export function SimulationProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const handleMessage = useCallback((msg) => {
    switch (msg.type) {
      case "full_snapshot":
        dispatch({ type: "FULL_SNAPSHOT", payload: msg });
        break;
      case "state_update":
        dispatch({ type: "STATE_UPDATE", payload: msg });
        break;
      case "comms_message":
        dispatch({ type: "COMMS_MESSAGE", payload: msg.message });
        break;
      case "game_over":
        dispatch({ type: "GAME_OVER", payload: msg });
        break;
      case "error":
        dispatch({ type: "ERROR", payload: msg.message });
        break;
      default:
        console.warn("Unknown WebSocket message type", msg.type);
    }
  }, []);

  const ws = useWebSocket(handleMessage);

  const selectAircraft = useCallback((id) => dispatch({ type: "SELECT_AIRCRAFT", payload: id }), []);
  const setView = useCallback((partial) => dispatch({ type: "SET_VIEW", payload: partial }), []);
  const toggle = useCallback((key) => dispatch({ type: "TOGGLE", payload: key }), []);
  const clearError = useCallback(() => dispatch({ type: "CLEAR_ERROR" }), []);

  const sendSimControl = useCallback(
    (action) => {
      if (action === "restart") dispatch({ type: "RESET_FOR_RESTART" });
      ws.sendSimControl(action);
    },
    [ws]
  );

  const value = useMemo(
    () => ({
      ...state,
      connectionStatus: ws.connectionStatus,
      sendCommand: ws.sendCommand,
      sendSimControl,
      setSpeed: ws.setSpeed,
      approveRequest: ws.approveRequest,
      denyRequest: ws.denyRequest,
      selectAircraft,
      setView,
      toggle,
      clearError,
    }),
    [state, ws, sendSimControl, selectAircraft, setView, toggle, clearError]
  );

  return <SimulationContext.Provider value={value}>{children}</SimulationContext.Provider>;
}

export function useSimulation() {
  const ctx = useContext(SimulationContext);
  if (!ctx) throw new Error("useSimulation must be used within a SimulationProvider");
  return ctx;
}
