<!--
SPDX-License-Identifier: Apache-2.0

Flat translucent grey quads, one per visible bond-filter plane - the direct
replacement for the original's manual "remove all actors, rebuild one
vtkActor/vtkMapper/vtkPolyData per bondFilterPoint" loop in
updateBondFilterActors(). Rebuilding every geometry on each change keeps the
same all-at-once-rebuild approach as the original rather than diffing, since
the number of filter planes is small.
-->
<script lang="ts">
  import { T } from '@threlte/core';
  import * as THREE from 'three';
  import { onDestroy } from 'svelte';

  interface BondFilterPoint {
    bondFilterPointString: number[];
  }

  interface Props {
    bondFilterPoints: BondFilterPoint[];
  }

  let { bondFilterPoints }: Props = $props();

  function buildGeometry(coords: number[]): THREE.BufferGeometry {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(coords), 3));
    // Same winding as the original's vtk polys [4, 0, 1, 2, 3] - one quad
    // split into two triangles.
    geometry.setIndex([0, 1, 2, 0, 2, 3]);
    geometry.computeVertexNormals();
    return geometry;
  }

  let planeGeometries: THREE.BufferGeometry[] = $state([]);

  // Plain (non-reactive) mirror of planeGeometries, used only to know what
  // to dispose next time. Reading the $state array itself inside the effect
  // below would make the effect depend on its own write, re-triggering
  // itself every time - an infinite loop.
  let previousGeometries: THREE.BufferGeometry[] = [];

  // Value-based snapshot of the last coordsList we built from. bondFilterPoints
  // may come from a computed getter that returns a *new* array reference with
  // the *same* values on every read - if the effect below only compared
  // references, that alone would make it re-run and rewrite state forever
  // (matches the infinite_loop_guard trip during hydration). Comparing
  // values instead makes the effect idempotent: given unchanged data, it's a
  // no-op no matter how many times it's re-triggered upstream.
  let lastCoordsList: number[][] = [];

  function coordsListsEqual(a: number[][], b: number[][]): boolean {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      const coordsA = a[i]!;
      const coordsB = b[i]!;
      if (coordsA.length !== coordsB.length) return false;
      for (let j = 0; j < coordsA.length; j++) {
        if (coordsA[j] !== coordsB[j]) return false;
      }
    }
    return true;
  }

  $effect(() => {
    const coordsList = bondFilterPoints
      .map((bondFilterPoint) => bondFilterPoint.bondFilterPointString)
      .filter((coords) => coords.length > 0);

    if (coordsListsEqual(coordsList, lastCoordsList)) return;
    lastCoordsList = coordsList;

    const next = coordsList.map(buildGeometry);
    for (const geometry of previousGeometries) geometry.dispose();
    previousGeometries = next;
    planeGeometries = next;
  });

  onDestroy(() => {
    for (const geometry of previousGeometries) geometry.dispose();
  });
</script>

{#each planeGeometries as geometry, index (index)}
  <T.Mesh {geometry}>
    <!-- Flat translucent grey plane - the old scene coloured these via a
         uniform 0.8 point scalar through vtk's default colour map, which
         renders as the same pale grey; setting it directly is simpler and
         avoids depending on that implicit default range. -->
    <T.MeshBasicMaterial color="#cccccc" transparent opacity={0.5} side={THREE.DoubleSide} />
  </T.Mesh>
{/each}
