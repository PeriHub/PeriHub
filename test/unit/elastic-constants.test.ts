// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import {
  convertElasticConstants,
  emptyElasticConstants,
  type ElasticConstants
} from '../../src/lib/utils/elastic-constants';

function withInputs(partial: Partial<ElasticConstants>): ElasticConstants {
  return { ...emptyElasticConstants(), ...partial };
}

describe('convertElasticConstants', () => {
  it('returns an empty result when fewer than two constants are given', () => {
    const result = convertElasticConstants(withInputs({ bulkModulus: 100 }));
    expect(result).toEqual(emptyElasticConstants());
  });

  it('returns an empty result when more than two constants are given', () => {
    const result = convertElasticConstants(
      withInputs({ bulkModulus: 100, youngsModulus: 200, shearModulus: 50 })
    );
    expect(result).toEqual(emptyElasticConstants());
  });

  it('derives the full set from bulk modulus + Young\'s modulus', () => {
    // Reference: steel-like isotropic material, K=160e9 Pa, E=200e9 Pa
    const K = 160e9;
    const E = 200e9;
    const result = convertElasticConstants(withInputs({ bulkModulus: K, youngsModulus: E }));

    expect(result.bulkModulus).toBeCloseTo(K, -6);
    expect(result.youngsModulus).toBeCloseTo(E, -6);
    // G = 3KE / (9K - E)
    expect(result.shearModulus).toBeCloseTo((3 * K * E) / (9 * K - E), -3);
    // v = (3K - E) / (6K)
    expect(result.poissonsRatio).toBeCloseTo((3 * K - E) / (6 * K), 6);
  });

  it('is consistent going bulk+shear -> Young/Poisson and back', () => {
    const K = 160e9;
    const G = 80e9;
    const forward = convertElasticConstants(withInputs({ bulkModulus: K, shearModulus: G }));

    expect(forward.youngsModulus).not.toBeNull();
    expect(forward.poissonsRatio).not.toBeNull();

    const backward = convertElasticConstants(
      withInputs({ youngsModulus: forward.youngsModulus, poissonsRatio: forward.poissonsRatio })
    );

    expect(backward.bulkModulus).toBeCloseTo(K, -3);
    expect(backward.shearModulus).toBeCloseTo(G, -3);
  });

  it('handles Lamé first parameter + shear modulus (regression: previous bug divided by λ·G instead of λ+G)', () => {
    const L = 100e9;
    const G = 80e9;
    const result = convertElasticConstants(withInputs({ lameFirst: L, shearModulus: G }));

    // E = G(3λ + 2G) / (λ + G)
    const expectedE = (G * (3 * L + 2 * G)) / (L + G);
    expect(result.youngsModulus).toBeCloseTo(expectedE, -3);
  });
});
