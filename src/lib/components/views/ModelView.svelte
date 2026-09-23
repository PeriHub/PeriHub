<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { RefreshCw, Maximize } from 'lucide-svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { getPointData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import ModelScene from '$lib/components/three/ModelScene.svelte';

  const modelData = $derived(modelStore.modelData);

  // Local view controls - mirrors the old component's own `data()`, not
  // shared app state (only the filtered results below live in viewStore).
  let resolution = $state(6);
  let radius = $state(0.2);
  let multiplier = $state(100);
  let pointString = $state<number[]>([1, 0, 0]);
  let blockIdString = $state<number[]>([1]);

  let scene: ModelScene | undefined = $state();

  const sphereRadius = $derived((radius * multiplier) / 100);

  function filterPointData() {
    let idx = 0;
    const filteredBlockIdStringTemp: number[] = [0];
    const filteredPointStringTemp: number[] = [0];
    const blocks = modelData.blocks;
    for (let i = 0; i < blockIdString.length; i++) {
      if (blocks[blockIdString[i]! * blocks.length - 1]?.show) {
        filteredBlockIdStringTemp[idx] = blockIdString[i]!;
        for (let j = 0; j < 3; j++) {
          filteredPointStringTemp[idx * 3 + j] = pointString[i * 3 + j]!;
        }
        idx += 1;
      }
    }
    viewStore.filteredBlockIdString = filteredBlockIdStringTemp;
    viewStore.filteredPointString = filteredPointStringTemp;
  }

  function updatePoints() {
    viewStore.modelLoading = true;
    filterPointData();
    viewStore.modelLoading = false;
  }

  async function getPointDataAndUpdateDx() {
    await getPointData({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName,
      ownModel: modelData.model.ownModel,
      ownMesh: modelData.model.ownMesh!,
      meshFile: modelData.model.meshFile!,
      twoD: modelData.model.twoDimensional
    })
      .then((response) => {
        pointString = response.points;
        blockIdString = response.block_ids;
        viewStore.dxValue = response.dx_value;
      })
      .catch((error) => notify.apiError(error));
  }

  async function viewPointData() {
    viewStore.modelLoading = true;
    await getPointDataAndUpdateDx();
    radius = parseFloat(viewStore.dxValue.toFixed(3));
    updatePoints();
    bus.emit('showHideBondFilters' as never);
    // The original called renderer.resetCamera() on every reload here (not
    // just once on first load) - fitToPoints() is the equivalent explicit
    // call, since CameraRig's own one-time auto-fit only covers first load.
    scene?.fitToPoints();
    viewStore.modelLoading = false;
  }

  onMount(() => {
    bus.on('viewPointData' as never, viewPointData);
    bus.on('filterPointData' as never, filterPointData);

    return () => {
      bus.off('viewPointData' as never, viewPointData);
      bus.off('filterPointData' as never, filterPointData);
    };
  });

  onDestroy(() => {
    bus.off('viewPointData' as never, viewPointData);
    bus.off('filterPointData' as never, filterPointData);
  });
</script>

<div class="flex h-full flex-col">
  <div class="flex items-center gap-1 border-b border-border bg-muted/30 px-2 py-1.5">
    {#if !modelData.model.ownModel}
      <Button variant="ghost" size="icon" onclick={viewPointData} title="Reload Model">
        <RefreshCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => scene?.resetCamera()} title="Reset Camera">
        <Maximize class="h-4 w-4" />
      </Button>
    {/if}

    <div class="mx-2 flex min-w-[140px] flex-1 items-center gap-2">
      <label for="model-view-radius" class="whitespace-nowrap text-xs text-muted-foreground">
        Radius: {multiplier}%
      </label>
      <input
        id="model-view-radius"
        type="range"
        min="1"
        max="200"
        step="1"
        bind:value={multiplier}
        onchange={updatePoints}
        class="flex-1 accent-primary"
      />
    </div>

    <div class="mx-2 flex min-w-[140px] flex-1 items-center gap-2">
      <label for="model-view-resolution" class="whitespace-nowrap text-xs text-muted-foreground">
        Resolution: {resolution}
      </label>
      <input
        id="model-view-resolution"
        type="range"
        min="3"
        max="20"
        step="1"
        bind:value={resolution}
        class="flex-1 accent-primary"
      />
    </div>
  </div>

  <div class="min-h-0 flex-1">
    <ModelScene
      bind:this={scene}
      points={viewStore.filteredPointString}
      blockIds={viewStore.filteredBlockIdString}
      radius={sphereRadius}
      {resolution}
      bondFilterPoints={viewStore.bondFilterPoints}
    />
  </div>
</div>
