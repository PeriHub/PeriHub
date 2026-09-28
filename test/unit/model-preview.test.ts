// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import {
  bcMarker,
  clipHalfplane,
  previewMargins,
  compileRegion,
  parseBcValue,
  previewViewBox,
  shapeOutline,
  type Bounds
} from '../../src/lib/utils/model-preview';

describe('parseBcValue', () => {
  it.each([
    ['0.5*t', 0.5],
    ['-100*t', -100],
    ['0*t', 0],
    ['0', 0],
    ['32e+3', 32000],
    [' -5 * t ', -5],
    [7, 7]
  ])('%s -> %s', (input, expected) => {
    expect(parseBcValue(input)).toBe(expected);
  });

  it.each(['sin(t)', 't*t', '', null, undefined])('%s is not a simple value', (input) => {
    expect(parseBcValue(input)).toBeNull();
  });
});

// Dogbone-like part: 0..13 x 0..2, grips at both x ends.
const model: Bounds = { minX: 0, maxX: 13, minY: 0, maxY: 2 };
const leftGrip: Bounds = { minX: 0, maxX: 1, minY: 0, maxY: 2 };
const rightGrip: Bounds = { minX: 12, maxX: 13, minY: 0, maxY: 2 };

describe('bcMarker', () => {
  it('pulls the right grip away from the part for a positive x value', () => {
    expect(bcMarker({ coordinate: 'x', value: '0.5*t' }, rightGrip, model)).toEqual({
      kind: 'arrow',
      x: 13,
      y: 1,
      dirX: 1,
      dirY: 0,
      outward: true
    });
  });

  it('pushes into the part for a positive x value on the left side', () => {
    expect(bcMarker({ coordinate: 'x', value: '10*t' }, leftGrip, model)).toMatchObject({
      kind: 'arrow',
      x: 0,
      dirX: 1,
      outward: false
    });
  });

  it('pulls the left grip outward for a negative x value', () => {
    expect(bcMarker({ coordinate: 'x', value: '-1*t' }, leftGrip, model)).toMatchObject({
      kind: 'arrow',
      x: 0,
      dirX: -1,
      outward: true
    });
  });

  it('uses the top edge for a y load on the upper block', () => {
    const top: Bounds = { minX: 5, maxX: 8, minY: 1.8, maxY: 2 };
    expect(bcMarker({ coordinate: 'y', value: '5*t' }, top, model)).toMatchObject({
      kind: 'arrow',
      x: 6.5,
      y: 2,
      dirY: 1,
      outward: true
    });
  });

  it('puts a load on a block spanning the part on the edge it pulls towards', () => {
    const fullHeight: Bounds = { minX: 0, maxX: 0.5, minY: 0, maxY: 2 };
    expect(bcMarker({ coordinate: 'y', value: '-100*t' }, fullHeight, model)).toMatchObject({
      kind: 'arrow',
      y: 0,
      dirY: -1,
      outward: true
    });
    expect(bcMarker({ coordinate: 'y', value: '100*t' }, fullHeight, model)).toMatchObject({
      y: 2,
      dirY: 1,
      outward: true
    });
  });

  it('marks a zero displacement as held fixed on the outer side', () => {
    expect(
      bcMarker({ coordinate: 'x', value: '0*t', variable: 'Displacements' }, leftGrip, model)
    ).toEqual({ kind: 'fixed', x: 0, y: 1, outX: -1, outY: 0 });
  });

  it('shows a zero force as a neutral point, not a support', () => {
    expect(
      bcMarker({ coordinate: 'y', value: '0', variable: 'Force Densities' }, leftGrip, model)
    ).toMatchObject({ kind: 'point' });
  });

  it('draws z-axis BCs as out-of-plane symbols', () => {
    expect(bcMarker({ coordinate: 'z', value: '-100' }, leftGrip, model)).toEqual({
      kind: 'outOfPlane',
      x: 0.5,
      y: 1,
      toward: false
    });
  });

  it('falls back to a neutral point for expressions it cannot read', () => {
    expect(bcMarker({ coordinate: 'x', value: 'sin(t)' }, rightGrip, model)).toEqual({
      kind: 'point',
      x: 12.5,
      y: 1
    });
  });

  it('ignores BCs without a usable axis', () => {
    expect(bcMarker({ coordinate: null, value: '1' }, rightGrip, model)).toBeNull();
  });
});

describe('shapeOutline', () => {
  it('projects a box to its x/y rectangle', () => {
    expect(shapeOutline({ role: 'add', type: 'box', min: [0, 1, -2], max: [4, 3, 2] })).toEqual({
      kind: 'rect',
      x: 0,
      y: 1,
      width: 4,
      height: 2
    });
  });

  it('draws spheres and ellipsoids as ellipses', () => {
    expect(shapeOutline({ role: 'remove', type: 'sphere', center: [1, 2, 0], radius: 3 })).toEqual({
      kind: 'ellipse',
      cx: 1,
      cy: 2,
      rx: 3,
      ry: 3
    });
    expect(
      shapeOutline({ role: 'add', type: 'ellipsoid', center: [0, 0, 0], radii: [2, 1, 5] })
    ).toMatchObject({ rx: 2, ry: 1 });
  });

  it('shows a cylinder along z as a circle and one in the plane as a rectangle', () => {
    const hole = { start: [5, 5, -1], end: [5, 5, 1], radius: 2 };
    expect(shapeOutline({ role: 'remove', type: 'cylinder', ...hole })).toEqual({
      kind: 'ellipse',
      cx: 5,
      cy: 5,
      rx: 2,
      ry: 2
    });
    const rod = shapeOutline({
      role: 'add',
      type: 'cylinder',
      start: [0, 0, 0],
      end: [10, 0, 0],
      radius: 1
    });
    expect(rod?.kind).toBe('polygon');
    const points = rod?.kind === 'polygon' ? rod.points : [];
    expect(points.map(([x, y]) => [Math.round(x), Math.round(y)])).toEqual([
      [0, 1],
      [10, 1],
      [10, -1],
      [0, -1]
    ]);
  });

  it('tapers a cone and passes polygons through', () => {
    const cone = shapeOutline({
      role: 'add',
      type: 'cone',
      start: [0, 0, 0],
      end: [0, 4, 0],
      radius_start: 2,
      radius_end: 0
    });
    expect(cone?.kind === 'polygon' && cone.points.map(([x]) => Math.round(x))).toEqual([
      -2, 0, 0, 2
    ]);
    expect(
      shapeOutline({
        role: 'remove',
        type: 'polygon',
        points: [
          [0, 0],
          [1, 0],
          [0, 1]
        ]
      })
    ).toEqual({
      kind: 'polygon',
      points: [
        [0, 0],
        [1, 0],
        [0, 1]
      ]
    });
  });
});

describe('previewViewBox', () => {
  it('fits the model inside the margin, centred, with y flipped', () => {
    // 13 x 2 model in 800 x 400 px with 50 px margin: width-limited, 700 px / 13 units.
    const box = previewViewBox(model, 800, 400, 50);
    expect(box.px).toBeCloseTo(13 / 700);
    expect(box.width).toBeCloseTo(800 * box.px);
    expect(box.height).toBeCloseTo(400 * box.px);
    expect(box.x + box.width / 2).toBeCloseTo(6.5);
    expect(box.y + box.height / 2).toBeCloseTo(-1);
  });

  it('is limited by height for tall models', () => {
    const tall: Bounds = { minX: 0, maxX: 1, minY: 0, maxY: 10 };
    expect(previewViewBox(tall, 800, 400, 50).px).toBeCloseTo(10 / 300);
  });

  it('centres the model between uneven margins', () => {
    const margins = { top: 60, right: 10, bottom: 20, left: 90 };
    const box = previewViewBox(model, 800, 400, margins);
    // 700 px available across: 13 units -> the model starts 90 px in from the left edge.
    expect(box.px).toBeCloseTo(13 / 700);
    expect((model.minX - box.x) / box.px).toBeCloseTo(90);
    // Vertically centred in the 320 px between top and bottom margins.
    expect((-model.maxY - box.y) / box.px).toBeCloseTo(60 + (320 - 2 / box.px) / 2);
  });

  it('does not collapse for a single point', () => {
    const box = previewViewBox({ minX: 1, maxX: 1, minY: 1, maxY: 1 }, 800, 400);
    expect(box.px).toBe(1);
    expect(box.width).toBeGreaterThan(0);
  });
});

describe('clipHalfplane', () => {
  const square: [number, number][] = [
    [0, 0],
    [10, 0],
    [10, 10],
    [0, 10]
  ];

  it('keeps the part where a*x + b*y <= c', () => {
    expect(clipHalfplane(square, 1, 0, 4)).toEqual([
      [0, 0],
      [4, 0],
      [4, 10],
      [0, 10]
    ]);
  });

  it('cuts a diagonal and drops everything when nothing is inside', () => {
    expect(clipHalfplane(square, 1, 1, 10)).toEqual([
      [0, 0],
      [10, 0],
      [0, 10]
    ]);
    expect(clipHalfplane(square, -1, 0, -20)).toEqual([]);
  });
});

describe('compileRegion', () => {
  const box = { minX: 0, maxX: 10, minY: 0, maxY: 4 };

  it('draws a half-plane as the clipped box, y flipped for SVG', () => {
    const { masks, root } = compileRegion({ type: 'halfplane', a: 1, b: 0, c: 2 }, box, 'm');
    expect(root).toBe('m-0');
    expect(masks).toEqual([
      { id: 'm-0', items: [{ kind: 'polygon', points: '0,0 2,0 2,-4 0,-4', fill: 'white' }] }
    ]);
  });

  it('nests masks for "and", draws each child for "or" and inverts for "not"', () => {
    const hp = (c: number) => ({ type: 'halfplane' as const, a: 1, b: 0, c });
    const { masks } = compileRegion(
      {
        type: 'or',
        children: [
          { type: 'and', children: [hp(2), hp(3)] },
          { type: 'not', child: hp(8) }
        ]
      },
      box,
      'm'
    );
    const byId = Object.fromEntries(masks.map((m) => [m.id, m.items]));
    expect(byId['m-0']).toEqual([
      { kind: 'masked', masks: ['m-1'], fill: 'white' },
      { kind: 'masked', masks: ['m-4'], fill: 'white' }
    ]);
    expect(byId['m-1']).toEqual([{ kind: 'masked', masks: ['m-2', 'm-3'], fill: 'white' }]);
    expect(byId['m-4']).toEqual([
      { kind: 'rect', x: 0, y: -4, width: 10, height: 4, fill: 'white' },
      { kind: 'masked', masks: ['m-5'], fill: 'black' }
    ]);
  });

  it('draws shapes by their outline and rasters as images', () => {
    const shape = compileRegion(
      { type: 'shape', shape: { role: 'add', type: 'sphere', center: [5, 2, 0], radius: 1 } },
      box,
      's'
    );
    expect(shape.masks[0]!.items).toEqual([
      { kind: 'ellipse', cx: 5, cy: -2, rx: 1, ry: 1, fill: 'white' }
    ]);
    const raster = compileRegion(
      { type: 'raster', x0: 0, y0: 0, width: 10, height: 4, png: 'AAAA' },
      box,
      'r'
    );
    expect(raster.masks[0]!.items).toEqual([
      { kind: 'image', x: 0, y: -4, width: 10, height: 4, href: 'data:image/png;base64,AAAA' }
    ]);
  });
});

describe('previewMargins', () => {
  it('gives room only to the sides that carry markers', () => {
    const margins = previewMargins(
      [
        { name: 'Pull', marker: { kind: 'arrow', x: 13, y: 1, dirX: 1, dirY: 0, outward: true } },
        { name: 'Top', marker: { kind: 'arrow', x: 6, y: 2, dirX: 0, dirY: 1, outward: true } },
        { name: 'Inside', marker: { kind: 'point', x: 6, y: 1 } }
      ],
      model
    );
    expect(margins.left).toBe(16);
    expect(margins.bottom).toBe(16);
    expect(margins.right).toBe(48 + (4 * 7) / 2 + 8);
    expect(margins.top).toBe(48 + 14 + 8);
  });
});
