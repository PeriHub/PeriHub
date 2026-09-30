// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

// Geometry for the model preview (ModelPreview.svelte): turns the coarse
// point cloud, block bounds and shape outlines from POST /models/{name}/preview
// plus the model's boundary conditions into what gets drawn. Kept out of the component so it can be
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
  /** A point of the block near its centroid - always on the block, even for rings and L shapes. */
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

/** One primitive of the model's geometry, as POST /models/{name}/preview describes it (shapes.py). */
export interface PreviewShape {
  role: 'add' | 'remove' | 'block';
  block_id?: number;
  type: 'box' | 'sphere' | 'ellipsoid' | 'cylinder' | 'cone' | 'polygon';
  min?: number[];
  max?: number[];
  center?: number[];
  radius?: number;
  radii?: number[];
  start?: number[];
  end?: number[];
  radius_start?: number;
  radius_end?: number;
  points?: number[][];
}

/** A shape's outline projected onto the x/y view plane, in model coordinates. */
export type Outline =
  | { kind: 'rect'; x: number; y: number; width: number; height: number }
  | { kind: 'ellipse'; cx: number; cy: number; rx: number; ry: number }
  | { kind: 'polygon'; points: [number, number][] };

export function shapeOutline(shape: PreviewShape): Outline | null {
  switch (shape.type) {
    case 'box': {
      const [min, max] = [shape.min, shape.max];
      if (!min || !max) return null;
      return {
        kind: 'rect',
        x: min[0]!,
        y: min[1]!,
        width: max[0]! - min[0]!,
        height: max[1]! - min[1]!
      };
    }
    case 'sphere':
    case 'ellipsoid': {
      const c = shape.center;
      if (!c) return null;
      const [rx, ry] = shape.radii ?? [shape.radius ?? 0, shape.radius ?? 0];
      return { kind: 'ellipse', cx: c[0]!, cy: c[1]!, rx: rx!, ry: ry! };
    }
    case 'cylinder':
    case 'cone': {
      const [s, e] = [shape.start, shape.end];
      if (!s || !e) return null;
      const r0 = shape.radius_start ?? shape.radius ?? 0;
      const r1 = shape.radius_end ?? shape.radius ?? 0;
      const [ax, ay] = [e[0]! - s[0]!, e[1]! - s[1]!];
      const len = Math.hypot(ax, ay);
      // Seen along its axis (the usual hole through a plate) it is a circle.
      if (len < 1e-9 * (Math.abs(e[2]! - s[2]!) || 1)) {
        const r = Math.max(r0, r1);
        return { kind: 'ellipse', cx: s[0]!, cy: s[1]!, rx: r, ry: r };
      }
      const [nx, ny] = [-ay / len, ax / len];
      return {
        kind: 'polygon',
        points: [
          [s[0]! + nx * r0, s[1]! + ny * r0],
          [e[0]! + nx * r1, e[1]! + ny * r1],
          [e[0]! - nx * r1, e[1]! - ny * r1],
          [s[0]! - nx * r0, s[1]! - ny * r0]
        ]
      };
    }
    case 'polygon':
      return shape.points
        ? { kind: 'polygon', points: shape.points.map((p) => [p[0]!, p[1]!]) }
        : null;
    default:
      return null;
  }
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
  // The edge nearer the outside of the part. When both are equally far out (a block spanning
  // the whole part along this axis), the edge in the load's direction: a pull downwards is
  // drawn at the bottom, not at the top.
  const [dHigh, dLow] = [modelHi - hi, lo - modelLo];
  const tie = Math.abs(dHigh - dLow) <= 1e-9 * (Math.abs(modelHi - modelLo) || 1);
  const outerIsHigh = tie ? value >= 0 : dHigh < dLow;
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

export interface Margins {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

/**
 * Room around the model for the BC markers, in pixels: only the sides a marker sits on get
 * space, sized for the arrow and its label (arrows are 12 units = 48 px long with their gap;
 * labels are ~12.8 px text). Sides without markers keep a small gap.
 */
export function previewMargins(
  markers: { name: string; marker: Marker }[],
  model: Bounds
): Margins {
  const margins: Margins = { top: 16, right: 16, bottom: 16, left: 16 };
  const charPx = 7;
  for (const { name, marker } of markers) {
    if (marker.kind === 'point' || marker.kind === 'outOfPlane') continue; // drawn inside the part
    const nearX = Math.min(marker.x - model.minX, model.maxX - marker.x);
    const nearY = Math.min(marker.y - model.minY, model.maxY - marker.y);
    const horizontal = marker.kind === 'arrow' ? marker.dirX !== 0 : marker.outX !== 0;
    const side: keyof Margins = horizontal
      ? marker.x - model.minX <= nearX
        ? 'left'
        : 'right'
      : marker.y - model.minY <= nearY
        ? 'bottom'
        : 'top';
    // Left/right labels sit beside the arrow tip, so half their width counts; top/bottom ones
    // above/below it, so their height does.
    const need = 48 + (horizontal ? (name.length * charPx) / 2 : 14) + 8;
    margins[side] = Math.max(margins[side], need);
  }
  return margins;
}

/**
 * SVG viewBox that fills a widthPx x heightPx box, with the model centred in the area left
 * inside `margin` (pixels, one value or per side; room for BC markers), and y flipped (draw
 * at -y). `px` is the size of one screen pixel in model units, so markers and text can be
 * sized in pixels regardless of model scale.
 */
export function previewViewBox(
  model: Bounds,
  widthPx: number,
  heightPx: number,
  margin: number | Margins = 70
) {
  const m =
    typeof margin === 'number'
      ? { top: margin, right: margin, bottom: margin, left: margin }
      : margin;
  const w = model.maxX - model.minX;
  const h = model.maxY - model.minY;
  const availW = Math.max(widthPx - m.left - m.right, 1);
  const availH = Math.max(heightPx - m.top - m.bottom, 1);
  const scale = Math.min(w > 0 ? availW / w : Infinity, h > 0 ? availH / h : Infinity);
  const px = Number.isFinite(scale) ? 1 / scale : 1;
  return {
    x: (model.minX + model.maxX) / 2 - (m.left + availW / 2) * px,
    y: -(model.minY + model.maxY) / 2 - (m.top + availH / 2) * px,
    width: widthPx * px,
    height: heightPx * px,
    px
  };
}

/** A preview region from POST /models/{name}/preview (support/model/regions.py). */
export type Region =
  | { type: 'all' }
  | { type: 'none' }
  | { type: 'halfplane'; a: number; b: number; c: number; strict?: boolean }
  | { type: 'shape'; shape: PreviewShape }
  | { type: 'and' | 'or'; children: Region[] }
  | { type: 'not'; child: Region }
  | { type: 'raster'; x0: number; y0: number; width: number; height: number; png: string };

/** What one SVG <mask> contains, in SVG coordinates (y already flipped). White = inside. */
export type MaskItem =
  | { kind: 'rect'; x: number; y: number; width: number; height: number; fill: string }
  | { kind: 'ellipse'; cx: number; cy: number; rx: number; ry: number; fill: string }
  | { kind: 'polygon'; points: string; fill: string }
  | { kind: 'image'; x: number; y: number; width: number; height: number; href: string }
  /** The bounding box, filled through the given masks (nested = intersection). */
  | { kind: 'masked'; masks: string[]; fill: string };

export interface MaskDef {
  id: string;
  items: MaskItem[];
}

/** Clip a convex polygon to a*x + b*y <= c (Sutherland–Hodgman against one line). */
export function clipHalfplane(
  polygon: [number, number][],
  a: number,
  b: number,
  c: number
): [number, number][] {
  const side = ([x, y]: [number, number]) => c - (a * x + b * y);
  const out: [number, number][] = [];
  polygon.forEach((p, i) => {
    const q = polygon[(i + 1) % polygon.length]!;
    const [sp, sq] = [side(p), side(q)];
    if (sp >= 0) out.push(p);
    if ((sp > 0 && sq < 0) || (sp < 0 && sq > 0)) {
      const t = sp / (sp - sq);
      out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
    }
  });
  return out;
}

const svgPoints = (points: [number, number][]) => points.map(([x, y]) => `${x},${-y}`).join(' ');

/**
 * Turn a region tree into flat SVG mask definitions: a shape, half-plane or raster is drawn
 * white; "and" nests masks, "or" draws each child through its own mask, "not" is the bounding
 * box minus the child. `box` (model coordinates) bounds everything, e.g. the half-planes.
 */
export function compileRegion(
  region: Region,
  box: Bounds,
  prefix: string
): { masks: MaskDef[]; root: string } {
  const masks: MaskDef[] = [];
  const corners: [number, number][] = [
    [box.minX, box.minY],
    [box.maxX, box.minY],
    [box.maxX, box.maxY],
    [box.minX, box.maxY]
  ];
  const full = (fill: string): MaskItem => ({
    kind: 'rect',
    x: box.minX,
    y: -box.maxY,
    width: box.maxX - box.minX,
    height: box.maxY - box.minY,
    fill
  });

  function items(r: Region): MaskItem[] {
    switch (r.type) {
      case 'all':
        return [full('white')];
      case 'none':
        return [];
      case 'halfplane': {
        const clipped = clipHalfplane(corners, r.a, r.b, r.c);
        return clipped.length > 2
          ? [{ kind: 'polygon', points: svgPoints(clipped), fill: 'white' }]
          : [];
      }
      case 'shape': {
        const o = shapeOutline(r.shape);
        if (!o) return [];
        if (o.kind === 'rect')
          return [
            {
              kind: 'rect',
              x: o.x,
              y: -(o.y + o.height),
              width: o.width,
              height: o.height,
              fill: 'white'
            }
          ];
        if (o.kind === 'ellipse')
          return [{ kind: 'ellipse', cx: o.cx, cy: -o.cy, rx: o.rx, ry: o.ry, fill: 'white' }];
        return [{ kind: 'polygon', points: svgPoints(o.points), fill: 'white' }];
      }
      case 'raster':
        return [
          {
            kind: 'image',
            x: r.x0,
            y: -(r.y0 + r.height),
            width: r.width,
            height: r.height,
            href: `data:image/png;base64,${r.png}`
          }
        ];
      case 'and':
        return [{ kind: 'masked', masks: r.children.map(define), fill: 'white' }];
      case 'or':
        return r.children.map((c) => ({ kind: 'masked', masks: [define(c)], fill: 'white' }));
      case 'not':
        return [full('white'), { kind: 'masked', masks: [define(r.child)], fill: 'black' }];
    }
  }

  function define(r: Region): string {
    const id = `${prefix}-${masks.length}`;
    const def: MaskDef = { id, items: [] };
    masks.push(def);
    def.items = items(r);
    return id;
  }

  return { masks, root: define(region) };
}
