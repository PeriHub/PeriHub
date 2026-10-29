<!--
Renders one InstancedMesh sphere per point, with per-instance color from the
`colorFor` callback. This is the direct replacement for vtkGlyph3DMapper:
instead of vtk.js re-running its glyphing pipeline, all spheres share one
geometry/material and are positioned + colored via raw instance buffers,
drawn in a single GPU draw call. `colorFor` is pluggable so this one
component serves both scenes - Results uses the continuous legend gradient
(valueToColor), Model uses the categorical block palette (blockIdToColor) -
the same way the original had two separate vtkColorTransferFunction LUTs
feeding the same Glyph3DMapper shape.
-->
<script lang="ts">
  import { T, useThrelte } from '@threlte/core';
  import * as THREE from 'three';
  import { onDestroy } from 'svelte';

  interface Props {
    // Flat [x0,y0,z0, x1,y1,z1, ...] - same layout as glyphPoints.setData() in
    // the original component.
    points: ArrayLike<number>;
    // One scalar per point - same role as glyphScalars in the original.
    values: ArrayLike<number>;
    radius: number;
    resolution: number;
    colorFor: (value: number, target: THREE.Color) => THREE.Color;
  }

  let { points, values, radius, resolution, colorFor }: Props = $props();

  // See the invalidate() calls below - on-demand rendering needs an
  // explicit nudge whenever we mutate instance buffers imperatively, since
  // Threlte can't observe that the way it observes declarative T.* props.
  const { invalidate } = useThrelte();

  let mesh: THREE.InstancedMesh | undefined = $state();

  const count = $derived(values.length);

  // Rebuilt only when resolution changes - equivalent to
  // sphereSource.setPhiResolution/setThetaResolution in the original.
  const geometry = $derived.by(() => new THREE.SphereGeometry(1, resolution, resolution));
  const material = new THREE.MeshStandardMaterial({ roughness: 0.6, metalness: 0.05 });

  // Reused scratch color - avoids allocating per point per update.
  const scratchColor = new THREE.Color();

  let previousGeometry: THREE.SphereGeometry | undefined;

  $effect(() => {
    if (!mesh) return;
    mesh.geometry = geometry;
    previousGeometry?.dispose();
    previousGeometry = geometry;
    invalidate();
  });

  // Equivalent of updateGlyphGeometry() + updateColorRange() combined: one
  // pass writing both instance buffers directly (a uniform scale + translation
  // matrix needs no Object3D.updateMatrix() per point - matters at 50k+ nodes).
  $effect(() => {
    if (!mesh || count === 0) return;
    const matrices = mesh.instanceMatrix.array as Float32Array;
    mesh.instanceColor ??= new THREE.InstancedBufferAttribute(new Float32Array(count * 3), 3);
    const colors = mesh.instanceColor.array as Float32Array;
    for (let i = 0; i < count; i++) {
      const m = i * 16;
      matrices.fill(0, m, m + 16);
      matrices[m] = matrices[m + 5] = matrices[m + 10] = radius;
      matrices[m + 12] = points[i * 3]!;
      matrices[m + 13] = points[i * 3 + 1]!;
      matrices[m + 14] = points[i * 3 + 2]!;
      matrices[m + 15] = 1;

      colorFor(values[i]!, scratchColor);
      scratchColor.toArray(colors, i * 3);
    }
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    mesh.computeBoundingSphere();
    invalidate();
  });

  onDestroy(() => {
    geometry.dispose();
    material.dispose();
  });
</script>

<!-- InstancedMesh's instance buffers are fixed-size at construction, so a
     change in point count (e.g. a new model loaded) needs a fresh instance -
     keyed on count to force that recreation, same trigger the original
     component handled by mutating vtkPoints in place instead. -->
{#key count}
  {#if count > 0}
    <T.InstancedMesh args={[geometry, material, count]} bind:ref={mesh} />
  {/if}
{/key}
