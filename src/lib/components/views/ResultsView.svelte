<script lang="ts">
  import { onMount, onDestroy, tick } from 'svelte';
  import type { Component } from 'svelte';
  import { Accordion, Dialog } from 'bits-ui';
  import {
    RotateCw,
    Maximize,
    ImageDown,
    SkipBack,
    Rewind,
    Pause,
    Play,
    FastForward,
    SkipForward,
    Settings,
    SlidersHorizontal,
    LoaderCircle
  } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { notify } from '$lib/utils/notify';
  import { bus } from '$lib/utils/bus';
  import { nodeSpacing } from '$lib/utils/node-spacing';
  import axios from 'axios';
  import { api } from '$lib/api/client';
  import { parseResultsFrame, type ResultsFrame } from '$lib/utils/results-frame';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import AccordionItem from '$lib/components/ui/AccordionItem.svelte';
  import VerticalColoredLegend from '$lib/components/views/VerticalColoredLegend.svelte';
  import ResultsScene from '$lib/components/views/ResultsScene.svelte';
  import CameraViewMenu from '$lib/components/three/CameraViewMenu.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import { drawColorBar } from '$lib/components/three/colorTransfer';
  import { downloadFile } from '$lib/utils/download';

  const modelData = $derived(modelStore.modelData);

  const AXIS_OPTIONS = ['X', 'Y', 'Z', 'Magnitude'];
  const FILTER_OPTIONS = ['Active', 'Temperature', 'Displacements', 'Damage'];

  const modelParams = $state({
    variable: 'Displacements',
    axis: 'Magnitude',
    displFactor: 1,
    step: 1,
    numberOfSteps: 100,
    // Additive (G-code) models keep every node of the final part in the mesh; unprinted ones stay at 0 K, so
    // filtering by Temperature shows the part as printed so far.
    filter: modelStore.modelData.additive?.length ? 'Temperature' : '',
    colorBarMin: null as number | null,
    colorBarMax: null as number | null
  });
  let variableOptions = $state<string[]>(['Displacements', 'Damage', 'Forces', 'Temperature']);

  let resolution = $state(8);
  let radius = $state(0.2);
  let dxValue = $state(0.2);
  let multiplier = $state(100);
  // Dark legend labels on light backgrounds (Rec. 709 luma of the hex).
  const legendLabelColor = $derived.by(() => {
    const [r, g, b] = [1, 3, 5].map((i) => parseInt(viewStore.sceneBackground.slice(i, i + 2), 16));
    return 0.2126 * r! + 0.7152 * g! + 0.0722 * b! > 140 ? '#1f2328' : 'white';
  });
  // Raw, not deep $state: a proxy per element would make every read in the render loop slow.
  let pointString = $state.raw<ArrayLike<number>>(new Float32Array([1, 0, 0]));
  let blockIdString = $state.raw<ArrayLike<number>>(new Float32Array([0]));
  let modelLoading = $state(false);
  let stepLoading = $state(false);
  let maxValue = $state(100);
  let minValue = $state(0);
  let time = $state(0);
  let playing = $state(false);
  let expansionValue = $state('');
  // Narrow screens only: the panel would cover the view, so it starts hidden.
  let showControls = $state(false);

  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  let dialogScreenshot = $state(false);
  let screenshotColorBar = $state(true);
  let screenshotTransparent = $state(false);

  function saveScreenshot() {
    dialogScreenshot = false;
    const image = scene?.snapshot(screenshotTransparent);
    if (!image) return;
    if (screenshotColorBar) {
      const scale = image.width / (viewport?.clientWidth || image.width);
      drawColorBar(image, minValue, maxValue, legendLabelColor, scale);
    }
    const name = `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}_${modelParams.variable}_step${modelParams.step}.png`;
    image.toBlob((blob) => blob && downloadFile(name, blob));
  }

  let scene: ResultsScene | undefined = $state();
  let viewport: HTMLDivElement | undefined = $state();

  const sphereRadius = $derived((radius * multiplier) / 100);

  // Frames of the current variable/axis/filter/... by step, so stepping back or replaying needs no request.
  // ponytail: LRU by Map insertion order, ~1 MB per frame at the 50k node cap.
  const CACHE_SIZE = 30;
  // Minimum time per frame while playing.
  const FRAME_MS = 200;
  const cache = new Map<number, Promise<ResultsFrame>>();
  let controller = new AbortController();
  // The step the view should end up on; responses for other steps are dropped.
  let wantedStep = 0;
  let spacingKnown = false;

  function loadFrame(step: number): Promise<ResultsFrame> {
    let frame = cache.get(step);
    if (frame) cache.delete(step);
    else
      frame = api
        .get<ArrayBuffer>('/results/points', {
          params: {
            model_name: modelStore.selectedModel.file,
            model_folder_name: modelData.model.modelFolderName,
            output: modelData.outputs[0]!.name,
            axis: modelParams.axis,
            step,
            displ_factor: modelParams.displFactor,
            variable: modelParams.variable,
            // At step 1 (time 0) nothing is printed yet - the filter would hide every node.
            filter: modelData.additive?.length && step === 1 ? '' : modelParams.filter,
            color_bar_min: modelParams.colorBarMin ?? undefined,
            color_bar_max: modelParams.colorBarMax ?? undefined,
            run_id: defaultStore.status.run_id
          },
          responseType: 'arraybuffer',
          signal: controller.signal
        })
        .then((response) => parseResultsFrame(response.data));
    const pending = frame;
    // Failed loads are retried on the next visit.
    pending.catch(() => cache.get(step) === pending && cache.delete(step));
    cache.set(step, pending);
    if (cache.size > CACHE_SIZE) cache.delete(cache.keys().next().value!);
    return pending;
  }

  function applyFrame(frame: ResultsFrame) {
    pointString = frame.points;
    blockIdString = frame.values;
    // Spacing barely moves between steps but costs O(100 n), so only after a reload.
    if (!spacingKnown) {
      dxValue = nodeSpacing(frame.points);
      radius = parseFloat(dxValue.toFixed(3));
      spacingKnown = true;
    }
    maxValue = frame.maxValue;
    minValue = frame.minValue;
    variableOptions = frame.variables;
    // The backend falls back to the first variable when the requested one is missing - mirror that here.
    if (!variableOptions.includes(modelParams.variable))
      modelParams.variable = variableOptions[0] ?? modelParams.variable;
    modelParams.numberOfSteps = frame.numberOfSteps;
    time = frame.time;
  }

  async function notifyError(error: unknown) {
    // With responseType arraybuffer, the JSON error body arrives as an ArrayBuffer too.
    const body = (error as { response?: { data?: unknown } }).response?.data;
    let detail = '';
    if (body instanceof ArrayBuffer) {
      try {
        detail = JSON.parse(new TextDecoder().decode(body)).detail ?? '';
      } catch {
        /* not JSON */
      }
    }
    notify.negative(detail || 'Loading results failed');
  }

  // Shows modelParams.step; the previous frame stays visible until the new one is there.
  async function showStep(loading = false) {
    const step = modelParams.step;
    wantedStep = step;
    modelLoading = loading;
    stepLoading = true;
    try {
      const frame = await loadFrame(step);
      if (step !== wantedStep) return;
      applyFrame(frame);
      if (step < modelParams.numberOfSteps) loadFrame(step + 1);
    } catch (error) {
      if (!axios.isCancel(error) && step === wantedStep) await notifyError(error);
    } finally {
      if (step === wantedStep) modelLoading = stepLoading = false;
    }
  }

  // Variable, axis, filter, ... changed: every cached or in-flight frame is stale.
  async function reload() {
    controller.abort();
    controller = new AbortController();
    cache.clear();
    spacingKnown = false;
    await showStep(true);
  }

  function debouncedReload() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(reload, 500);
  }

  // Waits for each frame, so a slow connection slows playback down instead of piling up requests.
  async function play() {
    playing = true;
    while (playing && modelParams.step < modelParams.numberOfSteps) {
      modelParams.step += 1;
      await Promise.all([showStep(), new Promise((resolve) => setTimeout(resolve, FRAME_MS))]);
    }
    playing = false;
  }

  function pause() {
    playing = false;
  }

  async function backward() {
    if (modelParams.step > 1) {
      modelParams.step -= 1;
      await showStep();
    }
  }

  async function fastBackward() {
    modelParams.step = 1;
    await showStep();
  }

  async function forward() {
    if (modelParams.step < modelParams.numberOfSteps) {
      modelParams.step += 1;
      await showStep();
    }
  }

  async function fastForward() {
    modelParams.step = modelParams.numberOfSteps;
    await showStep();
  }

  // Run finished: reload first (number_of_steps grew while it ran, cached frames may be stale), then jump to the
  // final step.
  async function refreshResults() {
    await reload();
    await fastForward();
  }

  onMount(async () => {
    bus.on('refreshResults' as never, refreshResults);
    // Just the data load - ResultsScene/Canvas handles its own sizing
    // (including the tab-mounted-but-hidden case), so no ResizeObserver
    // bookkeeping is needed here any more.
    await reload();
    // After data + tick, the scene ref and Three.js camera/controls are
    // ready — reset the camera so each tab visit starts at a clean framing
    // rather than restoring the user's last view.
    await tick();
    scene?.resetCamera();
  });

  onDestroy(() => {
    bus.off('refreshResults' as never, refreshResults);
    playing = false;
    controller.abort();
    clearTimeout(debounceTimer);
  });
</script>

<div class="relative flex h-full flex-col overflow-hidden">
  <div class="border-border bg-muted/30 flex flex-col gap-1 border-b px-2 py-1.5">
    <!-- Smaller buttons on narrow screens so all ten fit on one row. -->
    <div
      class="flex flex-wrap items-center gap-0.5 md:gap-1 [&_button]:size-8 md:[&_button]:size-9"
    >
      <Button variant="ghost" size="icon" onclick={reload} title="Reload Model">
        <RotateCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => scene?.resetCamera()} title="Reset Camera">
        <Maximize class="h-4 w-4" />
      </Button>
      <CameraViewMenu onSelect={(direction) => scene?.fitToPoints(direction)} />
      <Button
        variant="ghost"
        size="icon"
        onclick={() => (dialogScreenshot = true)}
        title="Save screenshot"
      >
        <ImageDown class="h-4 w-4" />
      </Button>
      <Button
        variant={showControls ? 'secondary' : 'ghost'}
        size="icon"
        class="md:hidden"
        onclick={() => (showControls = !showControls)}
        title="View options"
        aria-pressed={showControls}
      >
        <SlidersHorizontal class="h-4 w-4" />
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

      <div class="flex w-full min-w-[160px] items-center gap-2 px-2 md:ml-2 md:w-auto">
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
          oninput={() => cache.has(modelParams.step) && showStep()}
          onchange={() => showStep()}
          class="accent-primary flex-1"
        />
        <span
          class="text-muted-foreground flex shrink-0 items-center gap-1 text-xs whitespace-nowrap tabular-nums"
          title="Simulation time of this step"
        >
          {#if stepLoading}<LoaderCircle class="h-3 w-3 animate-spin" />{/if}
          t = {+time.toPrecision(3)}
        </span>
      </div>
    </div>
  </div>

  <div class="relative min-h-0 flex-1" bind:this={viewport}>
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
      class="border-border bg-background/90 absolute top-2 left-2 max-h-[calc(100%-1rem)] w-56 flex-col overflow-y-auto md:flex {showControls
        ? 'flex'
        : 'hidden'} gap-2 rounded-md border p-2 shadow-sm backdrop-blur-sm"
    >
      <div>
        <Label for="results-variable">Variable</Label>
        <Select id="results-variable" bind:value={modelParams.variable} onchange={reload}>
          {#each variableOptions as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </Select>
      </div>
      <div>
        <Label for="results-axis">Axis</Label>
        <Select id="results-axis" bind:value={modelParams.axis} onchange={reload}>
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
        <AccordionItem value="options" label="Options" icon={Settings as unknown as Component}>
          <div class="flex flex-col gap-2">
            <div>
              <Label for="results-filter">Filter</Label>
              <Select id="results-filter" bind:value={modelParams.filter} onchange={reload}>
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
            <div>
              <Label for="results-node-size">Node size: {multiplier}%</Label>
              <input
                id="results-node-size"
                type="range"
                min="1"
                max="200"
                step="1"
                bind:value={multiplier}
                class="accent-primary w-full"
              />
            </div>
            <div>
              <Label for="results-resolution">Resolution: {resolution}</Label>
              <input
                id="results-resolution"
                type="range"
                min="3"
                max="20"
                step="1"
                bind:value={resolution}
                class="accent-primary w-full"
              />
            </div>
            <div class="flex items-center justify-between gap-2">
              <Label for="results-background">Background</Label>
              <input
                id="results-background"
                type="color"
                bind:value={viewStore.sceneBackground}
                class="border-border h-7 w-12 cursor-pointer rounded border bg-transparent"
              />
            </div>
          </div>
        </AccordionItem>
      </Accordion.Root>
    </div>

    <div class="absolute right-2 bottom-2">
      <VerticalColoredLegend min={minValue} max={maxValue} labelColor={legendLabelColor} />
    </div>

    {#if modelLoading}
      <div class="bg-background/40 absolute inset-0 flex items-center justify-center">
        <LoaderCircle class="text-primary h-10 w-10 animate-spin" />
      </div>
    {/if}
  </div>
</div>

<Dialog.Root bind:open={dialogScreenshot}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,22rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">Save screenshot</Dialog.Title>
      <div class="space-y-3">
        <Toggle bind:checked={screenshotColorBar} label="Color bar" />
        <Toggle bind:checked={screenshotTransparent} label="Transparent background" />
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogScreenshot = false)}>Cancel</Button>
        <Button onclick={saveScreenshot}>Save PNG</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
