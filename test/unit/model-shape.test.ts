import { describe, expect, it } from 'vitest';
import defaultModel from '../../backend/app/assets/default_model.json';
import { isCurrentShape } from '../../src/lib/utils/model-shape';

// A pre-`params` config: PeriLab keys lived as camelCase fields directly on each entry.
const oldShapeModel = {
  blocks: [{ blocksId: 1, name: 'Part', materialModel: 'BC', horizon: 5 }],
  solvers: [{ solverId: 1, solvertype: 'Verlet', finalTime: 0.0005 }]
};

describe('isCurrentShape', () => {
  it('accepts the current default model (every block/solver has params)', () => {
    expect(isCurrentShape(defaultModel)).toBe(true);
  });

  it('rejects an old camelCase config', () => {
    expect(isCurrentShape(oldShapeModel)).toBe(false);
  });

  it('rejects a model whose solvers lack params even if blocks have them', () => {
    expect(
      isCurrentShape({
        blocks: [{ blocksId: 1, name: 'Part', params: {} }],
        solvers: [{ solverId: 1, solvertype: 'Verlet' }]
      })
    ).toBe(false);
  });

  it('rejects non-objects and null', () => {
    expect(isCurrentShape(null)).toBe(false);
    expect(isCurrentShape('old')).toBe(false);
    expect(isCurrentShape(undefined)).toBe(false);
  });

  it('a material (no blocks/solvers) is current-shape if it has params', () => {
    expect(isCurrentShape({ name: 'Steel', params: { "Young's Modulus": 200000 } })).toBe(true);
    expect(isCurrentShape({ name: 'Steel', youngsModulus: 200000 })).toBe(false);
  });
});
