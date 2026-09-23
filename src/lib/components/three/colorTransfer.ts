// SPDX-License-Identifier: Apache-2.0
//
// Piecewise-linear color interpolation, shared by both scenes:
// - valueToColor(): the continuous legend gradient (VerticalColoredLegend /
//   ResultsView), evaluated over an arbitrary [min, max] scalar range.
// - blockIdToColor(): the categorical block-id palette (ModelView), evaluated
//   over the backend's fixed [0, 1] normalized range.
// Both were separate vtkColorTransferFunction instances with their own
// addRGBPoint() stops in the original vtk.js code; same idea here, just two
// stop tables sharing one interpolator instead of two LUT objects.

import { Color } from 'three';

function buildInterpolator(stops: Color[]) {
  return function interpolate(t: number, target: Color = new Color()): Color {
    if (stops.length === 1) return target.copy(stops[0]);
    const clamped = Math.min(1, Math.max(0, t));
    const scaled = clamped * (stops.length - 1);
    const i0 = Math.floor(scaled);
    const i1 = Math.min(i0 + 1, stops.length - 1);
    const f = scaled - i0;
    return target.copy(stops[i0]).lerp(stops[i1], f);
  };
}

// Same 11 stops as VerticalColoredLegend.svelte's gradient, ordered low ->
// high (min -> max) instead of the legend's top-to-bottom (max -> min) order.
const LEGEND_STOPS = [
  '#5125ee',
  '#3f72f0',
  '#21a1e7',
  '#14c6c7',
  '#41da8a',
  '#7fe345',
  '#bae216',
  '#ded302',
  '#f3b500',
  '#fb8620',
  '#ec3c3f'
].map((hex) => new Color(hex));
const legendInterpolate = buildInterpolator(LEGEND_STOPS);

/**
 * Maps a scalar value in [min, max] to a color along the legend gradient.
 * Pass `target` to reuse an existing Color instance and avoid allocating
 * one per point per frame.
 */
export function valueToColor(
  value: number,
  min: number,
  max: number,
  target: Color = new Color()
): Color {
  if (!(max > min)) {
    return target.copy(LEGEND_STOPS[0]);
  }
  return legendInterpolate((value - min) / (max - min), target);
}

// Same 12 categorical RGB tuples (0-1 range) as the original ModelView's
// glyph LUT - distinct, perceptually separated colors for up to ~12 blocks.
const CATEGORICAL_STOPS = [
  [0.12, 0.47, 0.71], // Blue
  [0.84, 0.15, 0.16], // Red
  [0.2, 0.63, 0.17], // Green
  [0.96, 0.51, 0.07], // Orange
  [0.58, 0.22, 0.7], // Purple
  [0.89, 0.34, 0.61], // Pink
  [0.55, 0.35, 0.19], // Brown
  [0.5, 0.5, 0.5], // Grey
  [0.74, 0.74, 0.13], // Olive
  [0.09, 0.75, 0.81], // Cyan
  [0.9, 0.7, 0.04], // Gold
  [0.4, 0.65, 0.45] // Teal
].map(([r, g, b]) => new Color(r, g, b));
const categoricalInterpolate = buildInterpolator(CATEGORICAL_STOPS);

/**
 * Maps a backend-normalized block id (block_id / max_block_id, so already
 * in [0, 1]) to a color from the categorical palette.
 */
export function blockIdToColor(normalizedBlockId: number, target: Color = new Color()): Color {
  return categoricalInterpolate(normalizedBlockId, target);
}
