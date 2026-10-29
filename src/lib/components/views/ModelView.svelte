<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, Maximize } from 'lucide-svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { getPointData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import ModelScene from '$lib/components/three/ModelScene.svelte';
  import CameraViewMenu from '$lib/components/three/CameraViewMenu.svelte';

  const modelData = $derived(modelStore.modelData);
  const uploaded = $derived(modelData.model.meshSource === 'upload');
  // G-code is drawn as a toolpath by GcodeView, loaded on demand (gcode-preview bundles its own three.js).
  const gcodeFile = $derived(
    uploaded && modelData.discretization?.discType === 'gcode' ? modelData.model.meshFile : null
  );

  // Local view controls - mirrors the old component's own `data()`, not shared app state.
  let resolution = $state(8);
  let radius = $state(0.2);
  let multiplier = $state(100);
  // Raw: a deep proxy per element would slow the render loop down.
  let pointString = $state.raw<number[]>([1, 0, 0]);
  let blockIdString = $state.raw<number[]>([1]);

  let scene: ModelScene | undefined = $state();

  const sphereRadius = $derived((radius * multiplier) / 100);

  async function getPointDataAndUpdateDx() {
    await getPointData({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName,
      meshFile: uploaded ? (modelData.model.meshFile ?? undefined) : undefined,
      twoD: modelData.model.twoDimensional
    })
      .then((response) => {
        pointString = response.points;
        blockIdString = response.block_ids;
        radius = parseFloat(response.dx_value.toFixed(3));
      })
      .catch((error) => notify.apiError(error));
  }

  async function viewPointData() {
    if (gcodeFile) return;
    viewStore.modelLoading = true;
    await getPointDataAndUpdateDx();
    bus.emit('showHideBondFilters' as never);
    // The original called renderer.resetCamera() on every reload here (not
    // just once on first load) - fitToPoints() is the equivalent explicit
    // call, since CameraRig's own one-time auto-fit only covers first load.
    scene?.fitToPoints();
    viewStore.modelLoading = false;
  }

  onMount(() => {
    bus.on('viewPointData' as never, viewPointData);
    return () => bus.off('viewPointData' as never, viewPointData);
  });
</script>

{#if gcodeFile}
  {#await import('./GcodeView.svelte') then { default: GcodeView }}
    <GcodeView
      modelName={modelStore.selectedModel.file}
      folderName={modelData.model.modelFolderName}
      filename={gcodeFile}
    />
  {/await}
{:else}
  <div class="flex h-full flex-col">
    <div class="border-border bg-muted/30 flex flex-wrap items-center gap-1 border-b px-2 py-1.5">
      <Button variant="ghost" size="icon" onclick={viewPointData} title="Reload Model">
        <RefreshCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => scene?.resetCamera()} title="Reset Camera">
        <Maximize class="h-4 w-4" />
      </Button>
      <CameraViewMenu onSelect={(direction) => scene?.fitToPoints(direction)} />

      <!-- Own row below the buttons on narrow screens, inline from md up. -->
      <div class="flex w-full gap-4 px-2 md:w-auto md:flex-1">
        <div class="flex min-w-0 flex-1 items-center gap-2">
          <label for="model-view-radius" class="text-muted-foreground text-xs whitespace-nowrap">
            Radius: {multiplier}%
          </label>
          <input
            id="model-view-radius"
            type="range"
            min="1"
            max="200"
            step="1"
            bind:value={multiplier}
            class="accent-primary w-full min-w-0 flex-1"
          />
        </div>

        <div class="flex min-w-0 flex-1 items-center gap-2">
          <label
            for="model-view-resolution"
            class="text-muted-foreground text-xs whitespace-nowrap"
          >
            Resolution: {resolution}
          </label>
          <input
            id="model-view-resolution"
            type="range"
            min="3"
            max="20"
            step="1"
            bind:value={resolution}
            class="accent-primary w-full min-w-0 flex-1"
          />
        </div>
      </div>
    </div>

    <div class="min-h-0 flex-1">
      <ModelScene
        bind:this={scene}
        points={pointString}
        blockIds={blockIdString}
        radius={sphereRadius}
        {resolution}
        bondFilterPoints={viewStore.bondFilterPoints}
      />
    </div>
  </div>
{/if}
