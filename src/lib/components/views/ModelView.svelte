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

  // vtk.js has no type declarations for its per-class deep-import paths.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  type Any = any;

  const modelData = $derived(modelStore.modelData);

  // Local view controls - mirrors the old component's own `data()`, not
  // shared app state (only the filtered results below live in viewStore).
  let resolution = $state(6);
  let radius = $state(0.2);
  let multiplier = $state(100);
  let pointString = $state<number[]>([1, 0, 0]);
  let blockIdString = $state<number[]>([1]);

  let container: HTMLDivElement;
  let resizeObserver: ResizeObserver | null = null;
  let buildStarted = false;
  let sceneReady = $state(false);

  // vtk.js objects, created once in onMount and mutated in place afterwards.
  let fullScreenRenderer: Any;
  let renderer: Any;
  let renderWindow: Any;
  let sphereSource: Any;
  let glyphPoints: Any;
  let glyphScalars: Any;
  let glyphPolyData: Any;

  // vtk.js classes, dynamically imported once in buildScene() and reused
  // afterwards. Kept separate from the effects below (which must stay
  // synchronous - see updateBondFilterActors) rather than re-imported async
  // on every rebuild.
  let VtkActor: Any;
  let VtkMapper: Any;
  let VtkPolyData: Any;
  let VtkPoints: Any;

  // One actor per visible bond-filter plane, rebuilt whenever the derived
  // viewStore.bondFilterPoints changes. Tracked locally (not $state) since
  // these are imperative vtk.js objects, not data Svelte needs to diff.
  let bondFilterActors: Any[] = [];

  async function buildScene() {
    const [
      { default: vtkFullScreenRenderWindow },
      { default: vtkActor },
      { default: vtkMapper },
      { default: vtkGlyph3DMapper },
      { default: vtkSphereSource },
      { default: vtkPolyData },
      { default: vtkPoints },
      { default: vtkDataArray },
      { default: vtkColorTransferFunction }
    ] = await Promise.all([
      import('vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow'),
      import('vtk.js/Sources/Rendering/Core/Actor'),
      import('vtk.js/Sources/Rendering/Core/Mapper'),
      import('vtk.js/Sources/Rendering/Core/Glyph3DMapper'),
      import('vtk.js/Sources/Filters/Sources/SphereSource'),
      import('vtk.js/Sources/Common/DataModel/PolyData'),
      import('vtk.js/Sources/Common/Core/Points'),
      import('vtk.js/Sources/Common/Core/DataArray'),
      import('vtk.js/Sources/Rendering/Core/ColorTransferFunction'),
      // Side-effect only: registers the WebGL view-node implementations
      // (vtkOpenGLActor, vtkOpenGLPolyDataMapper, vtkOpenGLGlyph3DMapper...)
      // for the classes used below. Without these, vtkRenderWindow has no
      // representation to render our Actor/Mapper/Glyph3DMapper through, and
      // the render traversal crashes with "renNode is undefined".
      import('vtk.js/Sources/Rendering/Profiles/Geometry'),
      import('vtk.js/Sources/Rendering/Profiles/Glyph')
    ]);

    VtkActor = vtkActor;
    VtkMapper = vtkMapper;
    VtkPolyData = vtkPolyData;
    VtkPoints = vtkPoints;

    fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
      rootContainer: container,
      container,
      background: [45 / 255, 45 / 255, 45 / 255]
    });
    renderer = fullScreenRenderer.getRenderer();
    renderWindow = fullScreenRenderer.getRenderWindow();

    // Point-cloud glyph: one sphere per block point, coloured by block id -
    // the direct equivalent of the old <vtk-glyph-representation>.
    sphereSource = vtkSphereSource.newInstance({
      phiResolution: resolution,
      thetaResolution: resolution,
      radius: (radius * multiplier) / 100
    });

    glyphPoints = vtkPoints.newInstance();
    glyphScalars = vtkDataArray.newInstance({ name: 'blockId', numberOfComponents: 1, values: [0] });
    glyphPolyData = vtkPolyData.newInstance();
    glyphPolyData.setPoints(glyphPoints);
    glyphPolyData.getPointData().setScalars(glyphScalars);

    // Build a categorical color map for block IDs (normalized to 0-1 range by backend)
    // Use a set of distinct, perceptually separated colors for up to ~12 blocks
    const categoricalColors = [
      [0.12, 0.47, 0.71],  // Blue
      [0.84, 0.15, 0.16],  // Red
      [0.20, 0.63, 0.17],  // Green
      [0.96, 0.51, 0.07],  // Orange
      [0.58, 0.22, 0.70],  // Purple
      [0.89, 0.34, 0.61],  // Pink
      [0.55, 0.35, 0.19],  // Brown
      [0.50, 0.50, 0.50],  // Grey
      [0.74, 0.74, 0.13],  // Olive
      [0.09, 0.75, 0.81],  // Cyan
      [0.90, 0.70, 0.04],  // Gold
      [0.40, 0.65, 0.45],  // Teal
    ];

    const lut = vtkColorTransferFunction.newInstance();
    // Map normalized block IDs (1/N, 2/N, ..., 1.0) to distinct colors
    // We don't know N at build time, so create a piecewise map covering 0-1
    // with color stops at regular intervals
    const numColors = categoricalColors.length;
    for (let i = 0; i < numColors; i++) {
      const t = i / (numColors - 1); // 0.0, 0.09, 0.18, ..., 1.0
      const [r, g, b] = categoricalColors[i];
      lut.addRGBPoint(t, r, g, b);
    }

    const glyphMapper = vtkGlyph3DMapper.newInstance();
    glyphMapper.setScaling(false);
    glyphMapper.setInputData(glyphPolyData, 0);
    glyphMapper.setInputConnection(sphereSource.getOutputPort(), 1);
    // Backend normalizes block_ids to [0, 1] range (block_id / max_block_id)
    glyphMapper.setScalarRange(0, 1);
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
    const points = viewStore.filteredPointString;
    const blockIds = viewStore.filteredBlockIdString;
    glyphPoints.setData(Float32Array.from(points), 3);
    glyphScalars.setData(Float32Array.from(blockIds));
    glyphPolyData.modified();
    renderWindow?.render();
  }

  function updateSphereGeometry() {
    if (!sceneReady) return;
    sphereSource.setPhiResolution(resolution);
    sphereSource.setThetaResolution(resolution);
    sphereSource.setRadius((radius * multiplier) / 100);
    renderWindow?.render();
  }

  function updateBondFilterActors() {
    if (!sceneReady) return;
    // Read once, synchronously, so this stays a tracked $effect dependency.
    const bondFilterPoints = viewStore.bondFilterPoints;

    for (const actor of bondFilterActors) renderer.removeActor(actor);
    bondFilterActors = [];

    for (const bondFilterPoint of bondFilterPoints) {
      const coords = bondFilterPoint.bondFilterPointString;
      if (coords.length === 0) continue;

      const points = VtkPoints.newInstance();
      points.setData(Float32Array.from(coords), 3);

      const polyData = VtkPolyData.newInstance();
      polyData.setPoints(points);
      polyData.getPolys().setData(Uint16Array.from([4, 0, 1, 2, 3]));

      const mapper = VtkMapper.newInstance();
      mapper.setInputData(polyData);

      const actor = VtkActor.newInstance();
      actor.setMapper(mapper);
      // Flat translucent grey plane - the old scene coloured these via a
      // uniform 0.8 point scalar through vtk's default colour map, which
      // renders as the same pale grey; setting it directly is simpler and
      // avoids depending on that implicit default range.
      actor.getProperty().setColor(0.8, 0.8, 0.8);
      actor.getProperty().setOpacity(0.5);
      renderer.addActor(actor);
      bondFilterActors.push(actor);
    }

    renderWindow?.render();
  }

  async function viewPointData() {
    viewStore.modelLoading = true;
    await getPointDataAndUpdateDx();
    radius = parseFloat(viewStore.dxValue.toFixed(3));
    updatePoints();
    bus.emit('showHideBondFilters' as never);
    renderer?.resetCamera();
    viewStore.modelLoading = false;
  }

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

  $effect(() => {
    updateGlyphGeometry();
  });

  $effect(() => {
    updateSphereGeometry();
  });

  $effect(() => {
    updateBondFilterActors();
  });

  onMount(() => {
    // The "Model" tab panel stays mounted-but-hidden (display:none) when
    // another tab is active, so plain visibility isn't enough to know it's
    // safe to build the scene - vtkFullScreenRenderWindow renders once
    // synchronously on construction, and doing that against a container
    // whose layout hasn't resolved to a real size yet crashes deep inside
    // vtk.js's WebGL render pass. ResizeObserver only ever reports the
    // container's actual laid-out content box (and never fires at all while
    // it's display:none), so it doubles as both "wait until this tab is
    // first shown with a real size" and, after that, the ongoing resize
    // handler that used to live in buildScene().
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

    bus.on('viewPointData' as never, viewPointData);
    bus.on('filterPointData' as never, filterPointData);

    return () => {
      resizeObserver?.disconnect();
      bus.off('viewPointData' as never, viewPointData);
      bus.off('filterPointData' as never, filterPointData);
    };
  });

  onDestroy(() => {
    resizeObserver?.disconnect();
    fullScreenRenderer?.delete();
  });
</script>

<div class="flex h-full flex-col">
  <div class="flex items-center gap-1 border-b border-border bg-muted/30 px-2 py-1.5">
    {#if !modelData.model.ownModel}
      <Button variant="ghost" size="icon" onclick={viewPointData} title="Reload Model">
        <RefreshCw class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onclick={() => renderer?.resetCamera()} title="Reset Camera">
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

  <div bind:this={container} class="min-h-0 flex-1"></div>
</div>
