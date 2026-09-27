// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import {
  bcMarker,
  blockInfo,
  parseBcValue,
  previewViewBox,
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

describe('blockInfo', () => {
  it('puts the label on the block itself for a ring', () => {
    const ring = Array.from({ length: 16 }, (_, i) => (i / 16) * 2 * Math.PI);
    const [info] = blockInfo(
      ring.map((a) => Math.cos(a)),
      ring.map((a) => Math.sin(a)),
      ring.map(() => 1)
    );
    expect(Math.hypot(info!.labelX, info!.labelY)).toBeCloseTo(1);
  });

  it('groups points by block with bounds and a median label point', () => {
    const info = blockInfo([0, 1, 2, 10, 11], [0, 0, 1, 5, 6], [1, 1, 1, 2, 2]);
    expect(info).toEqual([
      { id: 1, bounds: { minX: 0, maxX: 2, minY: 0, maxY: 1 }, labelX: 1, labelY: 0 },
      { id: 2, bounds: { minX: 10, maxX: 11, minY: 5, maxY: 6 }, labelX: 11, labelY: 6 }
    ]);
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

  it('does not collapse for a single point', () => {
    const box = previewViewBox({ minX: 1, maxX: 1, minY: 1, maxY: 1 }, 800, 400);
    expect(box.px).toBe(1);
    expect(box.width).toBeGreaterThan(0);
  });
});
