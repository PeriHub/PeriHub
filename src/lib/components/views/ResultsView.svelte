<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  type Any = any;

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

  // Local view state - mirrors the old component's own `data()`.
  let resolution = $state(6);
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
  let initialCameraFit = false;

  let container: HTMLDivElement;
  let resizeObserver: ResizeObserver | null = null;
  let buildStarted = false;
  let sceneReady = $state(false);

  // vtk.js objects, created once in buildScene() and mutated in place.
  let fullScreenRenderer: Any;
  let renderer: Any;
  let renderWindow: Any;
  let sphereSource: Any;
  let glyphPoints: Any;
  let glyphScalars: Any;
  let glyphPolyData: Any;
  let glyphMapper: Any;
  let lut: Any;

  async function buildScene() {
    const [
      { default: vtkFullScreenRenderWindow },
      { default: vtkActor },
      { default: vtkGlyph3DMapper },
      { default: vtkSphereSource },
      { default: vtkPolyData },
      { default: vtkPoints },
      { default: vtkDataArray },
      { default: vtkColorTransferFunction }
    ] = await Promise.all([
      import('vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow'),
      import('vtk.js/Sources/Rendering/Core/Actor'),
      import('vtk.js/Sources/Rendering/Core/Glyph3DMapper'),
      import('vtk.js/Sources/Filters/Sources/SphereSource'),
      import('vtk.js/Sources/Common/DataModel/PolyData'),
      import('vtk.js/Sources/Common/Core/Points'),
      import('vtk.js/Sources/Common/Core/DataArray'),
      import('vtk.js/Sources/Rendering/Core/ColorTransferFunction'),
      // Side-effect only - registers the WebGL view-node implementation for
      // vtkGlyph3DMapper. Without it the render traversal has nothing to
      // draw the glyphs through and crashes with "renNode is undefined".
      import('vtk.js/Sources/Rendering/Profiles/Glyph')
    ]);

    fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
      rootContainer: container,
      container,
      background: [45 / 255, 45 / 255, 45 / 255]
    });
    renderer = fullScreenRenderer.getRenderer();
    renderWindow = fullScreenRenderer.getRenderWindow();

    sphereSource = vtkSphereSource.newInstance({
      phiResolution: resolution,
      thetaResolution: resolution,
      radius: (radius * multiplier) / 100
    });

    glyphPoints = vtkPoints.newInstance();
    glyphScalars = vtkDataArray.newInstance({ name: 'value', numberOfComponents: 1, values: [0] });
    glyphPolyData = vtkPolyData.newInstance();
    glyphPolyData.setPoints(glyphPoints);
    glyphPolyData.getPointData().setScalars(glyphScalars);

    lut = vtkColorTransferFunction.newInstance();
    lut.addRGBPoint(minValue, 0.231, 0.298, 0.752);
    lut.addRGBPoint((minValue + maxValue) / 2, 0.865, 0.865, 0.865);
    lut.addRGBPoint(maxValue, 0.706, 0.016, 0.15);

    glyphMapper = vtkGlyph3DMapper.newInstance();
    // Without this, Glyph3DMapper's default scaling falls back to the
    // active scalars array - the same one used for colouring - so every
    // glyph would be sized by its own value instead of rendered uniformly.
    glyphMapper.setScaling(false);
    glyphMapper.setInputData(glyphPolyData, 0);
    glyphMapper.setInputConnection(sphereSource.getOutputPort(), 1);
    glyphMapper.setScalarRange(minValue, maxValue);
    glyphMapper.setLookupTable(lut);

    const glyphActor = vtkActor.newInstance();
    glyphActor.setMapper(glyphMapper);
    renderer.addActor(glyphActor);

    sceneReady = true;
    renderWindow.render();
    renderer.resetCamera();
  }

  function updateGlyphGeometry() {
    if (!sceneReady) return;
    glyphPoints.setData(Float32Array.from(pointString), 3);
    glyphScalars.setData(Float32Array.from(blockIdString));
    glyphPolyData.modified();
    // Fit the camera once, the first time real geometry lands (buildScene's
    // own resetCamera() ran earlier against whatever placeholder point was
    // in state at construction time, usually before the API response
    // arrives). Without this the camera stays framed on that placeholder
    // and the actual point cloud renders completely outside view - i.e. an
    // empty-looking scene. Only done once, matching the old component's
    // one-time camera fit right after its initial load; later reloads
    // during playback intentionally leave the user's own pan/zoom alone.
    if (!initialCameraFit) {
      initialCameraFit = true;
      renderer.resetCamera();
    }
    renderWindow?.render();
  }

  function updateSphereGeometry() {
    if (!sceneReady) return;
    sphereSource.setPhiResolution(resolution);
    sphereSource.setThetaResolution(resolution);
    sphereSource.setRadius((radius * multiplier) / 100);
    renderWindow?.render();
  }

  function updateColorRange() {
    if (!sceneReady) return;
    // Glyph3DMapper is supposed to propagate setScalarRange() to the lookup
    // table's own range internally on its next rebuild, but rescaling the
    // vtkColorTransferFunction's stops directly with setMappingRange() is
    // the documented, guaranteed way to do it - relying only on the mapper
    // rebuilding at the right time was producing a stale colour scale as
    // the data's min/max changed between time steps (most values clamped
    // to one end of the old range).
    lut.setMappingRange(minValue, maxValue);
    glyphMapper.setScalarRange(minValue, maxValue);
    renderWindow?.render();
  }

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
    // are already applied reactively by updateSphereGeometry() above.
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
      filter: modelParams.filter || undefined,
      colorBarMin: modelParams.colorBarMin,
      colorBarMax: modelParams.colorBarMax
    })
      .then((response) => {
        pointString = response.nodes;
        blockIdString = response.value;
        dxValue = Math.hypot(pointString[3]! - pointString[0]!, pointString[4]! - pointString[1]!, pointString[5]! - pointString[2]!);
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
    timer = setInterval(forward, 1000);
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

  $effect(() => {
    updateGlyphGeometry();
  });

  $effect(() => {
    updateSphereGeometry();
  });

  $effect(() => {
    updateColorRange();
  });

  onMount(() => {
    // Kick the initial data load off immediately - it's just an HTTP call,
    // unrelated to whether the "Results" tab panel is currently visible.
    viewPointData(true);

    // The tab panel this view lives in stays mounted-but-hidden
    // (display:none) while another tab is active. vtkFullScreenRenderWindow
    // renders once synchronously on construction, and doing that against a
    // container whose layout hasn't resolved to a real size yet crashes
    // deep inside vtk.js's WebGL render pass. ResizeObserver only ever
    // reports the container's actual laid-out content box (and never fires
    // at all while it's display:none), so it doubles as both "wait until
    // this tab is first shown with a real size" and, after that, the
    // ongoing resize handler.
    resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0]!.contentRect;
      if (!buildStarted) {
        if (width > 0 && height > 0) {
          buildStarted = true;
          buildScene();
        }
        return;
      }
      fullScreenRenderer?.resize();
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver?.disconnect();
    };
  });

  onDestroy(() => {
    clearInterval(timer);
    clearTimeout(debounceTimer);
    fullScreenRenderer?.delete();
  });
</script>

<div class="relative flex h-full flex-col overflow-hidden">
  <div class="flex flex-col gap-1 border-b border-border bg-muted/30 px-2 py-1.5">
    <div class="flex flex-wrap items-center gap-1">
      <Button variant="ghost" size="icon" onclick={() => viewPointData(true)} title="Reload Model">
        <RotateCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => renderer?.resetCamera()} title="Reset Camera">
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

      <div class="ml-2 flex min-w-[120px] flex-1 items-center gap-2">
        <label for="results-step" class="whitespace-nowrap text-xs text-muted-foreground">
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
          class="flex-1 accent-primary"
        />
        <span class="w-16 shrink-0 whitespace-nowrap text-right text-xs text-muted-foreground">{time}</span>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-4">
      <div class="flex min-w-[160px] items-center gap-2">
        <label for="results-node-size" class="whitespace-nowrap text-xs text-muted-foreground">
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
          class="w-24 accent-primary"
        />
      </div>

      <div class="flex min-w-[160px] items-center gap-2">
        <label for="results-resolution" class="whitespace-nowrap text-xs text-muted-foreground">
          Resolution: {resolution}
        </label>
        <input
          id="results-resolution"
          type="range"
          min="3"
          max="20"
          step="1"
          bind:value={resolution}
          class="w-24 accent-primary"
        />
      </div>
    </div>
  </div>

  <div class="relative min-h-0 flex-1">
    <div bind:this={container} class="absolute inset-0"></div>

    <!-- Variable/axis/filter controls, floating over the 3D view like the
         old absolutely-positioned `.variables` panel. Positioned relative to
         this viewport wrapper (not the whole component), so it always sits
         at the top-left of the 3D view regardless of how many rows the
         toolbar above ends up needing. -->
    <div class="absolute left-2 top-2 flex w-56 flex-col gap-2 rounded-md border border-border bg-background/90 p-2 shadow-sm backdrop-blur-sm">
      <div>
        <Label for="results-variable">Variable</Label>
        <Select id="results-variable" bind:value={modelParams.variable} onchange={() => viewPointData(true)}>
          {#each variableOptions as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </Select>
      </div>
      <div>
        <Label for="results-axis">Axis</Label>
        <Select id="results-axis" bind:value={modelParams.axis} onchange={() => viewPointData(true)}>
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
              <Select id="results-filter" bind:value={modelParams.filter} onchange={() => viewPointData(true)}>
                <option value="">-</option>
                {#each FILTER_OPTIONS as option (option)}
                  <option value={option}>{option}</option>
                {/each}
              </Select>
            </div>
            <div>
              <Label for="results-min">Min.</Label>
              <Input id="results-min" type="number" bind:value={modelParams.colorBarMin} oninput={debouncedReload} />
            </div>
            <div>
              <Label for="results-max">Max.</Label>
              <Input id="results-max" type="number" bind:value={modelParams.colorBarMax} oninput={debouncedReload} />
            </div>
          </div>
        </AccordionItem>
      </Accordion.Root>
    </div>

    <div class="absolute bottom-2 left-2">
      <VerticalColoredLegend min={minValue} max={maxValue} />
    </div>

    {#if modelLoading}
      <div class="absolute inset-0 flex items-center justify-center bg-background/40">
        <LoaderCircle class="h-10 w-10 animate-spin text-primary" />
      </div>
    {/if}
  </div>
</div>
