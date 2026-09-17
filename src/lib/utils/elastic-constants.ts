// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export interface ElasticConstants {
  bulkModulus: number | null;
  shearModulus: number | null;
  youngsModulus: number | null;
  poissonsRatio: number | null;
  pWaveModulus: number | null;
  lameFirst: number | null;
}

export const emptyElasticConstants = (): ElasticConstants => ({
  bulkModulus: null,
  shearModulus: null,
  youngsModulus: null,
  poissonsRatio: null,
  pWaveModulus: null,
  lameFirst: null
});

/**
 * Converts a pair of isotropic elastic constants into the full set. Requires exactly two
 * of {bulkModulus, youngsModulus, lameFirst, shearModulus, poissonsRatio, pWaveModulus} to
 * be set on `input`; returns an empty result set otherwise.
 *
 * Ported from the original Quasar app's ConversionCard.vue — see the standard isotropic
 * elasticity conversion table (e.g. Wikipedia: "Elastic modulus" conversion formulae).
 */
export function convertElasticConstants(input: ElasticConstants): ElasticConstants {
  const known = Object.values(input).filter((v) => v != null).length;
  if (known !== 2) return emptyElasticConstants();

  const calculated = emptyElasticConstants();
  const K = input.bulkModulus;
  const E = input.youngsModulus;
  const L = input.lameFirst;
  const G = input.shearModulus;
  const v = input.poissonsRatio;
  const M = input.pWaveModulus;

  if (K != null) {
    calculated.bulkModulus = +K;
    if (E != null) {
      calculated.youngsModulus = +E;
      calculated.lameFirst = (3 * +K * (3 * +K - +E)) / (9 * +K - +E);
      calculated.shearModulus = (3 * +K * +E) / (9 * +K - +E);
      calculated.poissonsRatio = (3 * +K - +E) / (6 * +K);
      calculated.pWaveModulus = (3 * +K * (3 * +K + +E)) / (9 * +K - +E);
    }
    if (L != null) {
      calculated.youngsModulus = (9 * +K * (+K - +L)) / (3 * +K - +L);
      calculated.lameFirst = +L;
      calculated.shearModulus = (3 * +K - +L) / 2;
      calculated.poissonsRatio = +L / (3 * +K - +L);
      calculated.pWaveModulus = 3 * +K - 2 * +L;
    }
    if (G != null) {
      calculated.youngsModulus = (9 * +K * +G) / (3 * +K + +G);
      calculated.lameFirst = +K - (2 * +G) / 3;
      calculated.shearModulus = +G;
      calculated.poissonsRatio = (3 * +K - 2 * +G) / (2 * (3 * +K - +G));
      calculated.pWaveModulus = +K + (4 * +G) / 3;
    }
    if (v != null) {
      calculated.youngsModulus = 3 * +K * (1 - 2 * +v);
      calculated.lameFirst = (3 * +K * +v) / (1 + +v);
      calculated.shearModulus = (3 * +K * (1 - 2 * +v)) / (2 * (1 + +v));
      calculated.poissonsRatio = +v;
      calculated.pWaveModulus = (3 * +K * (1 - +v)) / (1 + +v);
    }
    if (M != null) {
      calculated.youngsModulus = (9 * +K * (+M - +K)) / (3 * +K + +M);
      calculated.lameFirst = (3 * +K - +M) / 2;
      calculated.shearModulus = (3 * (+M - +K)) / 4;
      calculated.poissonsRatio = (3 * +K - +M) / (3 * +K + +M);
      calculated.pWaveModulus = +M;
    }
  }
  if (E != null) {
    calculated.youngsModulus = +E;
    if (L != null) {
      const R = Math.sqrt(Math.pow(+E, 2) + 9 * Math.pow(+L, 2) + 2 * +E * +L);
      calculated.bulkModulus = (+E + 3 * +L + R) / 6;
      calculated.lameFirst = +L;
      calculated.shearModulus = (+E - 3 * +L + R) / 4;
      calculated.poissonsRatio = (2 * +L) / (+E + +L + R);
      calculated.pWaveModulus = (+E - +L + R) / 2;
    }
    if (G != null) {
      calculated.bulkModulus = (+E * +G) / (3 * (3 * +G - +E));
      calculated.lameFirst = (+G * (+E - 2 * +G)) / (3 * +G - +E);
      calculated.shearModulus = +G;
      calculated.poissonsRatio = +E / (2 * +G) - 1;
      calculated.pWaveModulus = (+G * (4 * +G - +E)) / (3 * +G - +E);
    }
    if (v != null) {
      calculated.bulkModulus = +E / (3 * (1 - 2 * +v));
      calculated.lameFirst = (+E * +v) / ((1 + +v) * (1 - 2 * +v));
      calculated.shearModulus = +E / (2 * (1.0 + +v));
      calculated.poissonsRatio = +v;
      calculated.pWaveModulus = (+E * (1 - +v)) / ((1 + +v) * (1 - 2 * +v));
    }
    if (M != null) {
      const S = Math.sqrt(Math.pow(+E, 2) + 9 * Math.pow(+M, 2) - 10 * +E * +M);
      calculated.bulkModulus = (3 * +M - +E + S) / 6;
      calculated.lameFirst = (+M - +E + S) / 4;
      calculated.shearModulus = (3 * +M + +E - S) / 8;
      calculated.poissonsRatio = (+E - +M + S) / (4 * +M);
      calculated.pWaveModulus = +M;
    }
  }
  if (L != null) {
    calculated.lameFirst = +L;
    if (G != null) {
      calculated.bulkModulus = +L + (2 * +G) / 3;
      calculated.youngsModulus = (+G * (3 * +L + 2 * +G)) / (+L + +G);
      calculated.shearModulus = +G;
      calculated.poissonsRatio = +L / (2 * (+L + +G));
      calculated.pWaveModulus = +L + 2 * +G;
    }
    if (v != null) {
      calculated.bulkModulus = (+L * (1 + +v)) / (3 * +v);
      calculated.youngsModulus = (+L * (1 + +v) * (1 - 2 * +v)) / +v;
      calculated.shearModulus = (+L * (1 - 2 * +v)) / (2 * +v);
      calculated.poissonsRatio = +v;
      calculated.pWaveModulus = (+L * (1 - +v)) / +v;
    }
    if (M != null) {
      calculated.bulkModulus = (+M + 2 * +L) / 3;
      calculated.youngsModulus = ((+M - +L) * (+M + 2 * +L)) / (+M + +L);
      calculated.shearModulus = (+M - +L) / 2;
      calculated.poissonsRatio = +L / (+M + +L);
      calculated.pWaveModulus = +M;
    }
  }
  if (G != null) {
    calculated.shearModulus = +G;
    if (v != null) {
      calculated.bulkModulus = (2 * +G * (1 + +v)) / (3 * (1 - 2 * +v));
      calculated.youngsModulus = 2 * +G * (1 + +v);
      calculated.lameFirst = (2 * +G * +v) / (1 - 2 * +v);
      calculated.poissonsRatio = +v;
      calculated.pWaveModulus = (2 * +G * (1 - +v)) / (1 - 2 * +v);
    }
    if (M != null) {
      calculated.bulkModulus = +M - (4 * +G) / 3;
      calculated.youngsModulus = (+G * (3 * +M - 4 * +G)) / (+M - +G);
      calculated.lameFirst = +M - 2 * +G;
      calculated.poissonsRatio = (+M - 2 * +G) / (2 * +M - 2 * +G);
      calculated.pWaveModulus = +M;
    }
  }
  if (v != null) {
    calculated.poissonsRatio = +v;
    if (M != null) {
      calculated.bulkModulus = (+M * (1 + +v)) / (3 * (1 - +v));
      calculated.youngsModulus = (+M * (1 + +v) * (1 - 2 * +v)) / (1 - +v);
      calculated.lameFirst = (+M * +v) / (1 - +v);
      calculated.shearModulus = (+M * (1 - 2 * +v)) / (2 * (1 - +v));
      calculated.pWaveModulus = +M;
    }
  }

  return calculated;
}
