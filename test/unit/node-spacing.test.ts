import { describe, expect, it } from 'vitest';
import { nodeSpacing } from '../../src/lib/utils/node-spacing';

describe('nodeSpacing', () => {
  it('finds the grid spacing regardless of node order', () => {
    const points: number[] = [];
    for (let x = 0; x < 20; x++) for (let y = 0; y < 10; y++) points.push(x * 0.5, y * 0.5, 0);
    // Consecutive nodes 0 and 1 are far apart after this shuffle - the old first-two-nodes estimate fails here.
    const shuffled: number[] = [];
    for (let k = 0; k < 200; k++) {
      const i = (k * 37) % 200;
      shuffled.push(points[3 * i]!, points[3 * i + 1]!, points[3 * i + 2]!);
    }
    expect(nodeSpacing(shuffled)).toBeCloseTo(0.5);
  });

  it('falls back to 1 without two distinct nodes', () => {
    expect(nodeSpacing([0, 0, 0])).toBe(1);
    expect(nodeSpacing([1, 1, 1, 1, 1, 1])).toBe(1);
  });
});
