<!--
SPDX-License-Identifier: Apache-2.0

Everything that must live INSIDE <Canvas> for the Results view - camera rig,
lights, background and the sphere cloud colored by the continuous legend
gradient.
-->
<script lang="ts">
  import { T } from '@threlte/core';
  import * as THREE from 'three';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import CameraRig from './CameraRig.svelte';
  import SphereCloud from './SphereCloud.svelte';
  import { valueToColor } from './colorTransfer';

  interface Props {
    points: number[];
    values: number[];
    radius: number;
    resolution: number;
    minValue: number;
    maxValue: number;
  }

  let { points, values, radius, resolution, minValue, maxValue }: Props = $props();

  let cameraRig: CameraRig | undefined = $state();

  // Called from the parent via bind:this={scene}; scene.resetCamera().
  export function resetCamera() {
    cameraRig?.resetCamera();
  }

  export function fitToPoints(direction?: [number, number, number]) {
    cameraRig?.fitToPoints(direction);
  }

  const colorFor = $derived((value: number, target: THREE.Color) =>
    valueToColor(value, minValue, maxValue, target)
  );
</script>

<CameraRig bind:this={cameraRig} {points} />

<T.AmbientLight intensity={0.7} />
<T.DirectionalLight position={[10, 10, 10]} intensity={0.9} />

<T.Color attach="background" args={[viewStore.sceneBackground]} />

<SphereCloud {points} {values} {radius} {resolution} {colorFor} />
