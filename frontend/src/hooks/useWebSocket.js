import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/simulation";

export function useWebSocket(onMessage) {
  const wsRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    let cancelled = false;
    let reconnectTimer = null;
    let attempt = 0;

    function connect() {
      if (cancelled) return;
      setConnectionStatus("connecting");
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        attempt = 0;
        setConnectionStatus("open");
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessageRef.current(data);
        } catch (err) {
          console.error("Failed to parse WebSocket message", err);
        }
      };
      ws.onclose = () => {
        if (cancelled) return;
        setConnectionStatus("closed");
        attempt += 1;
        const delay = Math.min(5000, 500 * attempt);
        reconnectTimer = setTimeout(connect, delay);
      };
      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, []);

  const sendRaw = useCallback((msg) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }, []);

  const sendCommand = useCallback(
    (aircraftId, command) => sendRaw({ type: "command", aircraft_id: aircraftId, command }),
    [sendRaw]
  );
  const sendSimControl = useCallback((action) => sendRaw({ type: "sim_control", action }), [sendRaw]);
  const setSpeed = useCallback((multiplier) => sendRaw({ type: "set_speed", multiplier }), [sendRaw]);
  const approveRequest = useCallback((requestId) => sendRaw({ type: "approve_request", request_id: requestId }), [sendRaw]);
  const denyRequest = useCallback((requestId) => sendRaw({ type: "deny_request", request_id: requestId }), [sendRaw]);

  return { connectionStatus, sendCommand, sendSimControl, setSpeed, approveRequest, denyRequest };
}
