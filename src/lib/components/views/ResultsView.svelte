<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy, tick } from 'svelte';
  import { Accordion } from 'bits-ui';
  import {
    RotateCw,
    Maximize,
    SkipBack,
    Rewind,
    Pause,
    Play,
    FastForward,
    SkipForward,
    Settings,
    LoaderCircle
  } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { notify } from '$lib/utils/notify';
  import { getPointDataResults } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import AccordionItem from '$lib/components/ui/AccordionItem.svelte';
  import VerticalColoredLegend from '$lib/components/views/VerticalColoredLegend.svelte';
  import ResultsScene from '$lib/components/views/ResultsScene.svelte';

  const modelData = $derived(modelStore.modelData);

  const AXIS_OPTIONS = ['X', 'Y', 'Z', 'Magnitude'];
  const FILTER_OPTIONS = ['Active', 'Temperature', 'Displacements', 'Damage'];

  const modelParams = $state({
    variable: 'Displacements',
    axis: 'Magnitude',
    displFactor: 1,
    step: 1,
    numberOfSteps: 100,
    filter: '',
    colorBarMin: null as number | null,
    colorBarMax: null as number | null
  });
  let variableOptions = $state<string[]>(['Displacements', 'Damage', 'Forces', 'Temperature']);

  let resolution = $state(8);
  let radius = $state(0.2);
  let dxValue = $state(0.2);
  let multiplier = $state(100);
  let pointString = $state<number[]>([1, 0, 0]);
  let blockIdString = $state<number[]>([0]);
  let modelLoading = $state(false);
  let maxValue = $state(100);
  let minValue = $state(0);
  let time = $state(0);
  let playing = $state(false);
  let expansionValue = $state('');

  let timer: ReturnType<typeof setInterval> | undefined;
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  let scene: ResultsScene | undefined = $state();

  const sphereRadius = $derived((radius * multiplier) / 100);

  async function viewPointData(loading = true) {
    modelLoading = loading;
    await getPointDataAndUpdateDx();
    radius = parseFloat(dxValue.toFixed(3));
    updatePoints();
    modelLoading = false;
  }

  function updatePoints() {
    // Kept as its own step (matching the old component) even though it's
    // currently a no-op beyond the loading flag - radius/resolution changes
    // are already applied reactively via props passed into ResultsScene.
    modelLoading = true;
    modelLoading = false;
  }

  async function getPointDataAndUpdateDx() {
    await getPointDataResults({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName!,
      cluster: modelData.job.cluster,
      output: modelData.outputs[0]!.name,
      tasks: modelData.job.tasks,
      axis: modelParams.axis,
      step: modelParams.step,
      displFactor: modelParams.displFactor,
      variable: modelParams.variable,
      filter: modelParams.filter,
      colorBarMin: modelParams.colorBarMin,
      colorBarMax: modelParams.colorBarMax
    })
      .then((response) => {
        pointString = response.nodes;
        blockIdString = response.value;
        dxValue = Math.hypot(
          pointString[3]! - pointString[0]!,
          pointString[4]! - pointString[1]!,
          pointString[5]! - pointString[2]!
        );
        maxValue = response.max_value;
        minValue = response.min_value;
        variableOptions = response.variables;
        modelParams.numberOfSteps = response.number_of_steps;
        time = response.time;
      })
      .catch((error) => notify.apiError(error));
  }

  function debouncedReload() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => viewPointData(true), 500);
  }

  function play() {
    playing = true;
    timer = setInterval(forward, 200);
  }

  function pause() {
    playing = false;
    clearInterval(timer);
  }

  async function backward() {
    if (modelParams.step > 1) {
      modelParams.step -= 1;
      await viewPointData(false);
    }
  }

  async function fastBackward() {
    modelParams.step = 1;
    await viewPointData(false);
  }

  async function forward() {
    if (modelParams.step < modelParams.numberOfSteps) {
      modelParams.step += 1;
      await viewPointData(false);
    } else {
      pause();
    }
  }

  async function fastForward() {
    modelParams.step = modelParams.numberOfSteps;
    await viewPointData(false);
  }

  onMount(async () => {
    // Just the data load - ResultsScene/Canvas handles its own sizing
    // (including the tab-mounted-but-hidden case), so no ResizeObserver
    // bookkeeping is needed here any more.
    await viewPointData(true);
    // After data + tick, the scene ref and Three.js camera/controls are
    // ready — reset the camera so each tab visit starts at a clean framing
    // rather than restoring the user's last view.
    await tick();
    scene?.resetCamera();
  });

  onDestroy(() => {
    clearInterval(timer);
    clearTimeout(debounceTimer);
  });
</script>

<div class="relative flex h-full flex-col overflow-hidden">
  <div class="border-border bg-muted/30 flex flex-col gap-1 border-b px-2 py-1.5">
    <div class="flex flex-wrap items-center gap-1">
      <Button variant="ghost" size="icon" onclick={() => viewPointData(true)} title="Reload Model">
        <RotateCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => scene?.resetCamera()} title="Reset Camera">
        <Maximize class="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        disabled={modelParams.step === 1}
        onclick={fastBackward}
        title="Fast Backward"
      >
        <SkipBack class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={backward} title="Backward">
        <Rewind class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" disabled={!playing} onclick={pause} title="Pause">
        <Pause class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" disabled={playing} onclick={play} title="Play">
        <Play class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={forward} title="Forward">
        <FastForward class="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        disabled={modelParams.step === modelParams.numberOfSteps}
        onclick={fastForward}
        title="Fast Forward"
      >
        <SkipForward class="h-4 w-4" />
      </Button>

      <div class="ml-2 flex min-w-[160px] items-center gap-2 px-2">
        <label for="results-step" class="text-muted-foreground text-xs whitespace-nowrap">
          Time Step: {modelParams.step}
        </label>
        <input
          id="results-step"
          type="range"
          min="0"
          max={modelParams.numberOfSteps}
          step="1"
          bind:value={modelParams.step}
          onchange={() => viewPointData(true)}
          class="accent-primary flex-1"
        />
        <span class="text-muted-foreground w-10 shrink-0 text-right text-xs whitespace-nowrap"
          >{time.toExponential(2)}</span
        >
      </div>
      <div class="flex min-w-[160px] items-center gap-2">
        <label for="results-node-size" class="text-muted-foreground text-xs whitespace-nowrap">
          Node Size: {multiplier}%
        </label>
        <input
          id="results-node-size"
          type="range"
          min="1"
          max="200"
          step="1"
          bind:value={multiplier}
          onchange={updatePoints}
          class="accent-primary w-24"
        />
      </div>

      <div class="flex min-w-[160px] items-center gap-2">
        <label for="results-resolution" class="text-muted-foreground text-xs whitespace-nowrap">
          Resolution: {resolution}
        </label>
        <input
          id="results-resolution"
          type="range"
          min="3"
          max="20"
          step="1"
          bind:value={resolution}
          class="accent-primary w-24"
        />
      </div>
    </div>
  </div>

  <div class="relative min-h-0 flex-1">
    <ResultsScene
      bind:this={scene}
      points={pointString}
      values={blockIdString}
      radius={sphereRadius}
      {resolution}
      {minValue}
      {maxValue}
    />

    <!-- Variable/axis/filter controls, floating over the 3D view like the
         old absolutely-positioned `.variables` panel. Positioned relative to
         this viewport wrapper (not the whole component), so it always sits
         at the top-left of the 3D view regardless of how many rows the
         toolbar above ends up needing. -->
    <div
      class="border-border bg-background/90 absolute top-2 left-2 flex w-56 flex-col gap-2 rounded-md border p-2 shadow-sm backdrop-blur-sm"
    >
      <div>
        <Label for="results-variable">Variable</Label>
        <Select
          id="results-variable"
          bind:value={modelParams.variable}
          onchange={() => viewPointData(true)}
        >
          {#each variableOptions as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </Select>
      </div>
      <div>
        <Label for="results-axis">Axis</Label>
        <Select
          id="results-axis"
          bind:value={modelParams.axis}
          onchange={() => viewPointData(true)}
        >
          {#each AXIS_OPTIONS as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </Select>
      </div>
      <div>
        <Label for="results-displ-factor">Displ. Magnitude</Label>
        <Input
          id="results-displ-factor"
          type="number"
          bind:value={modelParams.displFactor}
          oninput={debouncedReload}
        />
      </div>

      <Accordion.Root type="single" bind:value={expansionValue}>
        <AccordionItem value="options" label="Options" icon={Settings}>
          <div class="flex flex-col gap-2">
            <div>
              <Label for="results-filter">Filter</Label>
              <Select
                id="results-filter"
                bind:value={modelParams.filter}
                onchange={() => viewPointData(true)}
              >
                <option value="">-</option>
                {#each FILTER_OPTIONS as option (option)}
                  <option value={option}>{option}</option>
                {/each}
              </Select>
            </div>
            <div>
              <Label for="results-min">Min.</Label>
              <Input
                id="results-min"
                type="number"
                bind:value={modelParams.colorBarMin}
                oninput={debouncedReload}
              />
            </div>
            <div>
              <Label for="results-max">Max.</Label>
              <Input
                id="results-max"
                type="number"
                bind:value={modelParams.colorBarMax}
                oninput={debouncedReload}
              />
            </div>
          </div>
        </AccordionItem>
      </Accordion.Root>
    </div>

    <div class="absolute bottom-2 left-2">
      <VerticalColoredLegend min={minValue} max={maxValue} />
    </div>

    {#if modelLoading}
      <div class="bg-background/40 absolute inset-0 flex items-center justify-center">
        <LoaderCircle class="text-primary h-10 w-10 animate-spin" />
      </div>
    {/if}
  </div>
</div>
