<!--
SPDX-License-Identifier: Apache-2.0

Thin host for the <Canvas> - just forwards resetCamera()/fitToPoints() calls
down to Scene.svelte, which does the actual work. Kept as a separate outer
component because everything that calls useThrelte() (camera fitting,
invalidate() on manual buffer writes) has to be a genuine child of <Canvas>,
and this component itself, despite writing <Canvas> in its own template,
is not one - it's Canvas's parent.
-->
<script lang="ts">
  import { Canvas } from '@threlte/core';
  import Scene from '$lib/components/three/Scene.svelte';

  interface Props {
    points: number[];
    values: number[];
    radius: number;
    resolution: number;
    minValue: number;
    maxValue: number;
  }

  let { points, values, radius, resolution, minValue, maxValue }: Props = $props();

  let scene: Scene | undefined = $state();

  // Called from the parent via bind:this={scene}; scene.resetCamera().
  export function resetCamera() {
    scene?.resetCamera();
  }

  export function fitToPoints() {
    scene?.fitToPoints();
  }
</script>

<Canvas>
  <Scene bind:this={scene} {points} {values} {radius} {resolution} {minValue} {maxValue} />
</Canvas>
