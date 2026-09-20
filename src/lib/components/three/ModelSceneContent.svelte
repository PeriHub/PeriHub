<!--
SPDX-License-Identifier: Apache-2.0

Everything that must live INSIDE <Canvas> for the Model view - camera rig,
lights, background, the block-colored sphere cloud, and the bond-filter
planes.
-->
<script lang="ts">
  import { T } from '@threlte/core';
  import * as THREE from 'three';
  import CameraRig from './CameraRig.svelte';
  import SphereCloud from './SphereCloud.svelte';
  import BondFilterPlanes from './BondFilterPlanes.svelte';
  import { blockIdToColor } from './colorTransfer';

  interface BondFilterPoint {
    bondFilterPointString: number[];
  }

  interface Props {
    points: number[];
    blockIds: number[];
    radius: number;
    resolution: number;
    bondFilterPoints: BondFilterPoint[];
  }

  let { points, blockIds, radius, resolution, bondFilterPoints }: Props = $props();

  let cameraRig: CameraRig | undefined = $state();

  // Called from the parent via bind:this={scene}; scene.resetCamera() /
  // scene.fitToPoints().
  export function resetCamera() {
    cameraRig?.resetCamera();
  }

  export function fitToPoints() {
    cameraRig?.fitToPoints();
  }

  // Backend normalizes block_ids to [0, 1] already (block_id / max_block_id),
  // same as glyphMapper.setScalarRange(0, 1) in the original - no min/max
  // needed here, unlike the Results view's colorFor.
  function colorFor(value: number, target: THREE.Color) {
    return blockIdToColor(value, target);
  }
</script>

<CameraRig bind:this={cameraRig} {points} />

<T.AmbientLight intensity={0.7} />
<T.DirectionalLight position={[10, 10, 10]} intensity={0.9} />

<!-- Matches the original's background: [45/255, 45/255, 45/255] -->
<T.Color attach="background" args={['#2d2d2d']} />

<SphereCloud {points} values={blockIds} {radius} {resolution} {colorFor} />
<BondFilterPlanes {bondFilterPoints} />
