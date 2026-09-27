// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

// Geometry for the model preview (ModelPreview.svelte): turns the coarse
// point cloud from POST /generate/preview plus the model's boundary
// conditions into what gets drawn. Kept out of the component so it can be
// unit-tested (test/unit/model-preview.test.ts).

export type Axis = 'x' | 'y' | 'z';

export interface Bounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface BlockInfo {
  id: number;
  bounds: Bounds;
  /** The block's own point nearest its median - always on the block, even for rings and L shapes. */
  labelX: number;
  labelY: number;
}

export type Marker =
  | { kind: 'arrow'; x: number; y: number; dirX: number; dirY: number; outward: boolean }
  | { kind: 'fixed'; x: number; y: number; outX: number; outY: number }
  | { kind: 'outOfPlane'; x: number; y: number; toward: boolean }
  | { kind: 'point'; x: number; y: number };

export interface BoundaryConditionLike {
  name?: string | null;
  blockId?: number | null;
  coordinate?: string | null;
  value?: string | number | null;
  variable?: string | null;
}

const NUMBER = String.raw`[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?`;
const SIMPLE_VALUE = new RegExp(String.raw`^\s*(${NUMBER})\s*(?:\*\s*t)?\s*$`, 'i');

/**
 * Magnitude of a BC value like "0.5*t", "-100*t", "0" or "32e+3".
 * null for anything else (functions, tables) - the caller shows a neutral marker.
 */
export function parseBcValue(value: string | number | null | undefined): number | null {
  if (typeof value === 'number') return value;
  const m = SIMPLE_VALUE.exec(value ?? '');
  return m ? Number(m[1]) : null;
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)] ?? 0;
}

export function blockInfo(x: number[], y: number[], block: number[]): BlockInfo[] {
  const groups = new Map<number, { xs: number[]; ys: number[] }>();
  block.forEach((id, i) => {
    let g = groups.get(id);
    if (!g) groups.set(id, (g = { xs: [], ys: [] }));
    g.xs.push(x[i]!);
    g.ys.push(y[i]!);
  });
  return [...groups.entries()]
    .sort(([a], [b]) => a - b)
    .map(([id, { xs, ys }]) => {
      const mx = median(xs);
      const my = median(ys);
      let best = 0;
      for (let i = 1; i < xs.length; i++) {
        if (
          (xs[i]! - mx) ** 2 + (ys[i]! - my) ** 2 <
          (xs[best]! - mx) ** 2 + (ys[best]! - my) ** 2
        ) {
          best = i;
        }
      }
      return {
        id,
        bounds: {
          minX: Math.min(...xs),
          maxX: Math.max(...xs),
          minY: Math.min(...ys),
          maxY: Math.max(...ys)
        },
        labelX: xs[best]!,
        labelY: ys[best]!
      };
    });
}

/**
 * Where and how to draw one BC. The marker sits on the side of its block
 * that faces the nearest outside edge of the part along the BC's axis, so
 * a load on an end grip points away from the part (pull) or into it
 * (push) depending on its sign.
 */
export function bcMarker(bc: BoundaryConditionLike, block: Bounds, model: Bounds): Marker | null {
  const axis = bc.coordinate as Axis;
  if (axis !== 'x' && axis !== 'y' && axis !== 'z') return null;
  const midX = (block.minX + block.maxX) / 2;
  const midY = (block.minY + block.maxY) / 2;
  const value = parseBcValue(bc.value);
  if (value === null) return { kind: 'point', x: midX, y: midY };

  if (axis === 'z') {
    if (value === 0) return { kind: 'point', x: midX, y: midY };
    return { kind: 'outOfPlane', x: midX, y: midY, toward: value > 0 };
  }

  const [lo, hi, modelLo, modelHi] =
    axis === 'x'
      ? [block.minX, block.maxX, model.minX, model.maxX]
      : [block.minY, block.maxY, model.minY, model.maxY];
  const outerIsHigh = modelHi - hi <= lo - modelLo;
  const edge = outerIsHigh ? hi : lo;
  const at = axis === 'x' ? { x: edge, y: midY } : { x: midX, y: edge };
  const out = outerIsHigh ? 1 : -1;

  if (value === 0) {
    return bc.variable === 'Displacements'
      ? { kind: 'fixed', ...at, outX: axis === 'x' ? out : 0, outY: axis === 'y' ? out : 0 }
      : { kind: 'point', ...at };
  }
  const sign = Math.sign(value);
  return {
    kind: 'arrow',
    ...at,
    dirX: axis === 'x' ? sign : 0,
    dirY: axis === 'y' ? sign : 0,
    // Pointing away from the part = pull (arrow starts at the edge); otherwise push (arrow ends there).
    outward: sign === out
  };
}

/**
 * SVG viewBox that fills a widthPx x heightPx box, with the model centred,
 * scaled to fit inside `marginPx` of padding (room for BC markers), and y
 * flipped (draw at -y). `px` is the size of one screen pixel in model units,
 * so markers and text can be sized in pixels regardless of model scale.
 */
export function previewViewBox(model: Bounds, widthPx: number, heightPx: number, marginPx = 70) {
  const w = model.maxX - model.minX;
  const h = model.maxY - model.minY;
  const availW = Math.max(widthPx - 2 * marginPx, 1);
  const availH = Math.max(heightPx - 2 * marginPx, 1);
  const scale = Math.min(w > 0 ? availW / w : Infinity, h > 0 ? availH / h : Infinity);
  const px = Number.isFinite(scale) ? 1 / scale : 1;
  const width = widthPx * px;
  const height = heightPx * px;
  return {
    x: (model.minX + model.maxX) / 2 - width / 2,
    y: -(model.minY + model.maxY) / 2 - height / 2,
    width,
    height,
    px
  };
}
