// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { config } from '$lib/config';
import { modelStore } from './model-store.svelte';
import type { BondFilters } from '$lib/client';

interface BondFilterPoint {
  bondFilterPointsId: number;
  bondFilterPointString: number[];
}

interface PlotSeries {
  name: string;
  x: number[];
  y: number[];
  type: string;
}

function cross(a1: number, a2: number, a3: number, b1: number, b2: number, b3: number): number[] {
  return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1];
}

function vectorLength(a1: number, a2: number, a3: number): number {
  return Math.sqrt(a1 * a1 + a2 * a2 + a3 * a3);
}

function getVectorNorm(a1: number, a2: number, a3: number): number[] {
  const len = Math.abs(vectorLength(a1, a2, a3));
  return [a1 / len, a2 / len, a3 / len];
}

function computeBondFilterPoints(bondFilters: BondFilters[]): BondFilterPoint[] {
  const result: BondFilterPoint[] = [];

  for (let i = 0; i < bondFilters.length; i++) {
    const bondFilterPointString: number[] = [];
    const bf = bondFilters[i]!;

    if (bf.show) {
      const nx = bf.normalX,
        ny = bf.normalY,
        nz = bf.normalZ;

      if (bf.type === 'Disk') {
        const cx = bf.centerX,
          cy = bf.centerY,
          cz = bf.centerZ,
          radius = bf.radius;
        if (cx == null || cy == null || cz == null || radius == null) {
          console.log('Disk: cx, cy, cz, radius not defined');
          continue;
        }
        const vecs = [
          cross(nx, ny, nz, 1, 0, 0),
          cross(nx, ny, nz, 0, 1, 0),
          cross(nx, ny, nz, -1, 0, 0),
          cross(nx, ny, nz, 0, -1, 0)
        ].map((v) => getVectorNorm(v[0]!, v[1]!, v[2]!));

        for (const v of vecs) {
          bondFilterPointString.push(cx + v[0]! * radius, cy + v[1]! * radius, cz + v[2]! * radius);
        }
      } else {
        const lx = bf.lowerLeftCornerX,
          ly = bf.lowerLeftCornerY,
          lz = bf.lowerLeftCornerZ;
        const bx = bf.bottomUnitVectorX,
          by = bf.bottomUnitVectorY,
          bz = bf.bottomUnitVectorZ;
        const bl = bf.bottomLength,
          sl = bf.sideLength;

        if (
          lx == null || ly == null || lz == null ||
          bx == null || by == null || bz == null ||
          bl == null || sl == null
        ) {
          console.log('Rectangular_Plane: lx, ly, lz, bx, by, bz, bl, sl not defined');
          continue;
        }

        const point1 = [lx, ly, -lz];
        const [normx, normy, normz] = getVectorNorm(bx, by, bz);
        const point2 = [lx + normx! * bl, ly + normy! * bl, -lz + normz! * bl];

        const crossVector = cross(nx, ny, nz, bx, by, bz);
        const normVector = getVectorNorm(crossVector[0]!, crossVector[1]!, crossVector[2]!);

        const point4 = [
          lx + normVector[0]! * sl,
          ly + normVector[1]! * sl,
          -lz + normVector[2]! * sl
        ];
        const point3 = [
          point2[0]! + normVector[0]! * sl,
          point2[1]! + normVector[1]! * sl,
          point2[2]! + normVector[2]! * sl
        ];

        bondFilterPointString.push(...point1, ...point2, ...point3, ...point4);
      }
    }

    result.push({ bondFilterPointsId: i + 1, bondFilterPointString });
  }

  return result;
}

class ViewStore {
  viewId = $state('image');
  textId = $state('input');
  modelImg = $state(`${config.apiBase}/assets/images/Dogbone.jpg`);
  modelLoading = $state(false);
  textLoading = $state(false);
  textOutput = $state('');
  logOutput = $state('');
  // Derived from modelStore.modelData.bondFilters - no manual mutation needed
  bondFilterPoints = $derived<BondFilterPoint[]>(computeBondFilterPoints(modelStore.modelData.bondFilters ?? []));
  filteredPointString = $state([1, 0, 0]);
  filteredBlockIdString = $state([1]);
  dxValue = $state(0.1);
  resultPort = $state<number | null>(null);
  plotData = $state<PlotSeries[]>([
    {
      name: 'Displacement',
      x: [1, 2, 3, 4],
      y: [10, 15, 20, 17],
      type: 'scatter'
    }
  ]);
  plotLayout = $state({
    title: 'Model',
    showlegend: true,
    legend: { orientation: 'h' },
    hovermode: 'compare',
    bargap: 0,
    xaxis: { showgrid: true, zeroline: true, color: 'white', title: 'Time' },
    yaxis: { showgrid: true, zeroline: true, color: 'white', title: 'Displacement' },
    plot_bgcolor: '#2D2D2D',
    paper_bgcolor: '#2D2D2D',
    font: { color: 'white' },
    modebar: { color: 'white' }
  });
  jsonData = $state({});
}

export const viewStore = new ViewStore();
