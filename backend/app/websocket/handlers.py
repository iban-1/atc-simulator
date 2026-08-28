from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.aircraft import AltitudeCommand, HeadingCommand, LandCommand, RouteCommand, SpeedCommand
from app.simulation.session import SimulationSession

router = APIRouter()

COMMAND_KIND_MODELS = {
    "heading": HeadingCommand,
    "altitude": AltitudeCommand,
    "speed": SpeedCommand,
    "route": RouteCommand,
    "land": LandCommand,
}

SIM_CONTROL_ACTIONS = {"start", "pause", "resume", "restart"}


@router.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket) -> None:
    session: SimulationSession = websocket.app.state.session
    await session.manager.connect(websocket)
    await session.manager.send(websocket, session.build_full_snapshot())

    try:
        while True:
            raw = await websocket.receive_json()
            await _dispatch(session, websocket, raw)
    except WebSocketDisconnect:
        session.manager.disconnect(websocket)


async def _dispatch(session: SimulationSession, websocket: WebSocket, raw: dict) -> None:
    msg_type = raw.get("type")
    try:
        if msg_type == "command":
            _handle_command(session, raw)
        elif msg_type == "approve_request":
            session.engine.approve_request(raw["request_id"])
        elif msg_type == "deny_request":
            session.engine.deny_request(raw["request_id"])
        elif msg_type == "sim_control":
            _handle_sim_control(session, raw)
        elif msg_type == "set_speed":
            session.engine.set_speed(raw["multiplier"])
        else:
            raise ValueError(f"Unknown message type: {msg_type}")
    except (ValueError, KeyError, TypeError) as exc:
        await session.manager.send(websocket, {"type": "error", "message": str(exc)})
        return

    await session.manager.broadcast(session.build_state_update())


def _handle_command(session: SimulationSession, raw: dict) -> None:
    command_payload = raw["command"]
    kind = command_payload.get("kind")
    model_cls = COMMAND_KIND_MODELS.get(kind)
    if model_cls is None:
        raise ValueError(f"Unknown command kind: {kind}")
    command = model_cls(**command_payload)
    session.engine.apply_command(raw["aircraft_id"], command)


def _handle_sim_control(session: SimulationSession, raw: dict) -> None:
    action = raw["action"]
    if action not in SIM_CONTROL_ACTIONS:
        raise ValueError(f"Unknown sim control action: {action}")
    getattr(session.engine, action)()
    if action == "restart":
        session._comms_sent = 0
        session._game_over_sent = False
