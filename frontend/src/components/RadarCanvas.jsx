import { useEffect, useRef, useState } from "react";
import { useSimulation } from "../hooks/useSimulation.jsx";
import { clampZoom, screenToSim, simToScreen } from "../services/radarTransform.js";

const RING_STEP_NM = 20;
const RING_COUNT = 5;
const CLICK_HIT_RADIUS_PX = 12;

const CONFLICT_COLOR = {
  none: "#22d38a",
  caution: "#fbbf24",
  warning: "#f87171",
};

export default function RadarCanvas() {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const dragRef = useRef({ dragging: false, moved: false, lastX: 0, lastY: 0 });
  const [size, setSize] = useState({ width: 800, height: 600 });

  const {
    stateUpdate,
    waypoints,
    airspaceBounds,
    trails,
    view,
    toggles,
    selectedAircraftId,
    selectAircraft,
    setView,
    scenario,
  } = useSimulation();

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setSize({ width: entry.contentRect.width, height: entry.contentRect.height });
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;

    canvas.width = size.width * dpr;
    canvas.height = size.height * dpr;
    canvas.style.width = `${size.width}px`;
    canvas.style.height = `${size.height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const fullView = { ...view, canvasWidth: size.width, canvasHeight: size.height };
    draw(ctx, size, fullView, {
      aircraft: stateUpdate?.aircraft ?? [],
      conflicts: stateUpdate?.conflicts ?? [],
      waypoints,
      airspaceBounds,
      trails,
      toggles,
      selectedAircraftId,
      sectors: scenario?.sectors ?? [],
    });
  }, [size, view, stateUpdate, waypoints, airspaceBounds, trails, toggles, selectedAircraftId, scenario]);

  function handleWheel(e) {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    setView({ pixelsPerNm: clampZoom(view.pixelsPerNm * factor) });
  }

  function handleMouseDown(e) {
    dragRef.current = { dragging: true, moved: false, lastX: e.clientX, lastY: e.clientY };
  }

  function handleMouseMove(e) {
    const d = dragRef.current;
    if (!d.dragging) return;
    const dx = e.clientX - d.lastX;
    const dy = e.clientY - d.lastY;
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) d.moved = true;
    if (d.moved) {
      setView({
        centerX: view.centerX - dx / view.pixelsPerNm,
        centerY: view.centerY + dy / view.pixelsPerNm,
      });
    }
    d.lastX = e.clientX;
    d.lastY = e.clientY;
  }

  function handleMouseUp(e) {
    const d = dragRef.current;
    dragRef.current = { dragging: false, moved: false, lastX: 0, lastY: 0 };
    if (d.moved) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;
    const fullView = { ...view, canvasWidth: size.width, canvasHeight: size.height };

    const aircraft = stateUpdate?.aircraft ?? [];
    let closest = null;
    let closestDist = Infinity;
    for (const ac of aircraft) {
      const [sx, sy] = simToScreen(ac.x, ac.y, fullView);
      const dist = Math.hypot(sx - px, sy - py);
      if (dist < closestDist) {
        closestDist = dist;
        closest = ac;
      }
    }
    if (closest && closestDist <= CLICK_HIT_RADIUS_PX) {
      selectAircraft(closest.id);
    }
  }

  return (
    <div ref={containerRef} className="relative h-full w-full overflow-hidden bg-radar-bg">
      <canvas
        ref={canvasRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => (dragRef.current = { dragging: false, moved: false, lastX: 0, lastY: 0 })}
        className="cursor-crosshair"
      />
      <RadarToggles />
    </div>
  );
}

function RadarToggles() {
  const { toggles, toggle } = useSimulation();
  const items = [
    ["labels", "Labels"],
    ["trails", "Trails"],
    ["routes", "Routes"],
    ["waypoints", "Waypoints"],
    ["sectors", "Sectors"],
  ];
  return (
    <div className="absolute right-2 top-2 flex gap-1 rounded bg-zinc-950/80 p-1 text-[10px]">
      {items.map(([key, label]) => (
        <button
          key={key}
          onClick={() => toggle(key)}
          className={`rounded px-2 py-1 ${toggles[key] ? "bg-emerald-700 text-white" : "bg-zinc-800 text-zinc-400"}`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function draw(ctx, size, view, data) {
  const { aircraft, conflicts, waypoints, airspaceBounds, trails, toggles, selectedAircraftId, sectors } = data;

  ctx.fillStyle = "#03110a";
  ctx.fillRect(0, 0, size.width, size.height);

  drawRangeRings(ctx, view);
  drawCompass(ctx, size, view);
  if (airspaceBounds) drawAirspaceBoundary(ctx, view, airspaceBounds);
  if (toggles.sectors) drawSectors(ctx, view, sectors);
  if (toggles.waypoints) drawWaypoints(ctx, view, waypoints);

  const conflictAircraftIds = new Set();
  conflicts.forEach((c) => {
    conflictAircraftIds.add(c.aircraft_a);
    conflictAircraftIds.add(c.aircraft_b);
  });

  if (toggles.trails) {
    for (const ac of aircraft) {
      drawTrail(ctx, view, trails[ac.id]);
    }
  }

  if (toggles.routes) {
    for (const ac of aircraft) {
      if (ac.id === selectedAircraftId) drawRoute(ctx, view, ac, waypoints);
    }
  }

  for (const ac of aircraft) {
    drawAircraft(ctx, view, ac, waypoints, {
      selected: ac.id === selectedAircraftId,
      showLabel: toggles.labels,
    });
  }

  drawConflictLines(ctx, view, conflicts, aircraft);
}

function drawRangeRings(ctx, view) {
  const [cx, cy] = simToScreen(view.centerX, view.centerY, view);
  ctx.strokeStyle = "#0e3324";
  ctx.lineWidth = 1;
  ctx.font = "10px monospace";
  ctx.fillStyle = "#1f5c40";
  for (let i = 1; i <= RING_COUNT; i++) {
    const radiusNm = i * RING_STEP_NM;
    const r = radiusNm * view.pixelsPerNm;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillText(`${radiusNm}NM`, cx + r + 2, cy - 2);
  }
  // crosshair at center
  ctx.beginPath();
  ctx.moveTo(cx - 6, cy);
  ctx.lineTo(cx + 6, cy);
  ctx.moveTo(cx, cy - 6);
  ctx.lineTo(cx, cy + 6);
  ctx.stroke();
}

function drawCompass(ctx, size, view) {
  const maxR = RING_COUNT * RING_STEP_NM * view.pixelsPerNm;
  const [cx, cy] = simToScreen(view.centerX, view.centerY, view);
  ctx.fillStyle = "#3fae7d";
  ctx.font = "bold 12px monospace";
  ctx.textAlign = "center";
  const labels = [
    ["N", 0, -maxR],
    ["S", 0, maxR],
    ["E", maxR, 0],
    ["W", -maxR, 0],
  ];
  for (const [label, dx, dy] of labels) {
    ctx.fillText(label, cx + dx, cy + dy);
  }
  ctx.textAlign = "left";
}

function drawAirspaceBoundary(ctx, view, bounds) {
  const [minX, minY, maxX, maxY] = bounds;
  const [x1, y1] = simToScreen(minX, maxY, view);
  const [x2, y2] = simToScreen(maxX, minY, view);
  ctx.strokeStyle = "#2a6b4a";
  ctx.setLineDash([6, 4]);
  ctx.lineWidth = 1.5;
  ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
  ctx.setLineDash([]);
}

function drawSectors(ctx, view, sectorList) {
  if (!sectorList || sectorList.length === 0) return;
  ctx.font = "10px monospace";
  for (const sector of sectorList) {
    if (!sector.boundary || sector.boundary.length === 0) continue;
    ctx.beginPath();
    sector.boundary.forEach(([sx, sy], i) => {
      const [x, y] = simToScreen(sx, sy, view);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.strokeStyle = "rgba(113, 113, 122, 0.5)";
    ctx.lineWidth = 1;
    ctx.stroke();

    const [lx, ly] = simToScreen(sector.boundary[0][0], sector.boundary[0][1], view);
    ctx.fillStyle = "#71717a";
    ctx.fillText(sector.name, lx + 4, ly + 12);
  }
}

function drawWaypoints(ctx, view, waypoints) {
  ctx.font = "10px monospace";
  for (const wp of waypoints) {
    const [x, y] = simToScreen(wp.x, wp.y, view);
    ctx.fillStyle = wp.kind === "airport" ? "#60a5fa" : "#71717a";
    if (wp.kind === "airport") {
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.moveTo(x, y - 5);
      ctx.lineTo(x + 5, y + 4);
      ctx.lineTo(x - 5, y + 4);
      ctx.closePath();
      ctx.fill();
    }
    ctx.fillStyle = "#a1a1aa";
    ctx.fillText(wp.name, x + 8, y + 3);
  }
}

function drawTrail(ctx, view, points) {
  if (!points || points.length < 2) return;
  ctx.beginPath();
  points.forEach((p, i) => {
    const [x, y] = simToScreen(p.x, p.y, view);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "rgba(34, 211, 138, 0.35)";
  ctx.lineWidth = 1.5;
  ctx.stroke();
}

function drawRoute(ctx, view, aircraft, waypoints) {
  const remaining = aircraft.route.slice(aircraft.route_index);
  if (remaining.length === 0) return;
  ctx.beginPath();
  const [sx, sy] = simToScreen(aircraft.x, aircraft.y, view);
  ctx.moveTo(sx, sy);
  for (const wpId of remaining) {
    const wp = waypoints.find((w) => w.id === wpId);
    if (!wp) continue;
    const [x, y] = simToScreen(wp.x, wp.y, view);
    ctx.lineTo(x, y);
  }
  ctx.strokeStyle = "rgba(96, 165, 250, 0.6)";
  ctx.setLineDash([4, 4]);
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.setLineDash([]);
}

function drawAircraft(ctx, view, ac, waypoints, { selected, showLabel }) {
  const [x, y] = simToScreen(ac.x, ac.y, view);
  const color = ac.emergency ? "#ef4444" : CONFLICT_COLOR[ac.conflict_status] ?? CONFLICT_COLOR.none;

  if (ac.emergency) {
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x, y, 13, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((ac.heading_deg * Math.PI) / 180);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(0, -7);
  ctx.lineTo(5, 6);
  ctx.lineTo(0, 3);
  ctx.lineTo(-5, 6);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  if (selected) {
    ctx.strokeStyle = "#fde047";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.stroke();
  }

  if (showLabel) {
    ctx.fillStyle = color;
    ctx.font = "10px monospace";
    ctx.fillText(ac.callsign, x + 9, y - 4);
    ctx.fillStyle = "#a1a1aa";
    ctx.fillText(`FL${Math.round(ac.altitude_ft / 100)} ${Math.round(ac.speed_kt)}kt`, x + 9, y + 8);
  }
}

function drawConflictLines(ctx, view, conflicts, aircraft) {
  const byId = new Map(aircraft.map((a) => [a.id, a]));
  for (const w of conflicts) {
    const a = byId.get(w.aircraft_a);
    const b = byId.get(w.aircraft_b);
    if (!a || !b) continue;
    const [ax, ay] = simToScreen(a.x, a.y, view);
    const [bx, by] = simToScreen(b.x, b.y, view);
    ctx.strokeStyle = w.is_active_violation ? "#f87171" : w.risk_level === "warning" ? "#fb923c" : "#fbbf24";
    ctx.setLineDash([3, 3]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(bx, by);
    ctx.stroke();
    ctx.setLineDash([]);
  }
}
