// Pure NM <-> pixel transforms for the radar canvas.
// Sim coordinates: x = East(+)/West(-) NM, y = North(+)/South(-) NM, origin at
// airspace center. Screen coordinates grow down, so Y is flipped.

export function simToScreen(x, y, view) {
  const px = view.canvasWidth / 2 + (x - view.centerX) * view.pixelsPerNm;
  const py = view.canvasHeight / 2 - (y - view.centerY) * view.pixelsPerNm;
  return [px, py];
}

export function screenToSim(px, py, view) {
  const x = (px - view.canvasWidth / 2) / view.pixelsPerNm + view.centerX;
  const y = -(py - view.canvasHeight / 2) / view.pixelsPerNm + view.centerY;
  return [x, y];
}

export const MIN_PIXELS_PER_NM = 1.5;
export const MAX_PIXELS_PER_NM = 20;

export function clampZoom(pixelsPerNm) {
  return Math.min(MAX_PIXELS_PER_NM, Math.max(MIN_PIXELS_PER_NM, pixelsPerNm));
}
