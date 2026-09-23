<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Canvas } from '@threlte/core';
  import ModelSceneContent from './ModelSceneContent.svelte';

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

  let content: ModelSceneContent | undefined = $state();

  // Called from the parent via bind:this={scene}; scene.resetCamera().
  export function resetCamera() {
    content?.resetCamera();
  }

  export function fitToPoints() {
    content?.fitToPoints();
  }
</script>

<Canvas>
  <ModelSceneContent bind:this={content} {points} {blockIds} {radius} {resolution} {bondFilterPoints} />
</Canvas>
