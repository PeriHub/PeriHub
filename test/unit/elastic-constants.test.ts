// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import {
  convertElasticConstants,
  emptyElasticConstants,
  orthotropicStiffness,
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

  it("derives the full set from bulk modulus + Young's modulus", () => {
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

describe('orthotropicStiffness', () => {
  it('reduces to the isotropic Lamé stiffness when all directions match', () => {
    const E = 200;
    const nu = 0.3;
    const G = E / (2 * (1 + nu));
    const C = orthotropicStiffness(E, E, E, G, G, G, nu, nu, nu);
    const lambda = (E * nu) / ((1 + nu) * (1 - 2 * nu));
    expect(C.C11).toBeCloseTo(lambda + 2 * G);
    expect(C.C22).toBeCloseTo(lambda + 2 * G);
    expect(C.C33).toBeCloseTo(lambda + 2 * G);
    expect(C.C12).toBeCloseTo(lambda);
    expect(C.C13).toBeCloseTo(lambda);
    expect(C.C23).toBeCloseTo(lambda);
    expect(C.C44).toBeCloseTo(G);
    expect(C.C16).toBe(0);
  });

  it('inverts an anisotropic compliance block', () => {
    const [E1, E2, E3, nu12, nu13, nu23] = [150, 10, 12, 0.3, 0.25, 0.4];
    const C = orthotropicStiffness(E1, E2, E3, 5, 5, 3, nu12, nu13, nu23);
    const S = [
      [1 / E1, -nu12 / E1, -nu13 / E1],
      [-nu12 / E1, 1 / E2, -nu23 / E2],
      [-nu13 / E1, -nu23 / E2, 1 / E3]
    ];
    const Cm = [
      [C.C11!, C.C12!, C.C13!],
      [C.C12!, C.C22!, C.C23!],
      [C.C13!, C.C23!, C.C33!]
    ];
    for (let i = 0; i < 3; i++)
      for (let j = 0; j < 3; j++)
        expect(S[i]!.reduce((acc, _, k) => acc + S[i]![k]! * Cm[k]![j]!, 0)).toBeCloseTo(
          i === j ? 1 : 0
        );
  });
});
