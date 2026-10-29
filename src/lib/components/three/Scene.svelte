<!--
Everything that must live INSIDE <Canvas> for the Results view - camera rig,
lights, background and the sphere cloud colored by the continuous legend
gradient.
-->
<script lang="ts">
  import { T, useThrelte } from '@threlte/core';
  import * as THREE from 'three';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import CameraRig from './CameraRig.svelte';
  import SphereCloud from './SphereCloud.svelte';
  import { valueToColor } from './colorTransfer';

  interface Props {
    points: ArrayLike<number>;
    values: ArrayLike<number>;
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

  const { renderer, scene, camera, invalidate } = useThrelte();

  // The current view as a 2D canvas. Rendered here and copied in the same task, so the WebGL drawing buffer
  // needs no preserveDrawingBuffer; the renderer has alpha, so no background means transparent pixels.
  export function snapshot(transparent: boolean): HTMLCanvasElement {
    const background = scene.background;
    if (transparent) scene.background = null;
    renderer.render(scene, camera.current);
    const source = renderer.domElement;
    const image = document.createElement('canvas');
    image.width = source.width;
    image.height = source.height;
    image.getContext('2d')!.drawImage(source, 0, 0);
    scene.background = background;
    invalidate();
    return image;
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
