<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  // Drawn from the model itself (POST /generate/preview) instead of a
  // hand-made image per model: blocks coloured and numbered, boundary
  // conditions as arrows/supports. Parameter changes refetch the coarse
  // point cloud (debounced); BC/block edits only redraw.
  import { previewModel, type PreviewResponse } from '$lib/client';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { modelNeedsRefresh } from '$lib/utils/modelSync';
  import { blockIdToColor } from '$lib/components/three/colorTransfer';
  import {
    bcMarker,
    blockInfo,
    previewViewBox,
    type Bounds,
    type Marker
  } from '$lib/utils/model-preview';

  let cloud = $state<PreviewResponse | null>(null);
  let loading = $state(false);
  let error = $state('');
  let requestId = 0;
  let widthPx = $state(0);
  let heightPx = $state(0);

  const ownModel = $derived(modelStore.modelData.model.ownModel);

  // Only inputs the generator reads trigger a request.
  const geometryKey = $derived(
    JSON.stringify([
      modelStore.selectedModel.file,
      modelStore.modelParams,
      modelStore.modelData.model,
      modelStore.modelData.discretization
    ])
  );

  $effect(() => {
    void geometryKey;
    // Mid-switch, config/valves may still belong to the previous model.
    if (ownModel || modelNeedsRefresh(modelStore.selectedModel.file)) return;
    const timer = setTimeout(load, 500);
    return () => clearTimeout(timer);
  });

  async function load() {
    const id = ++requestId;
    loading = true;
    try {
      const result = await previewModel({
        modelName: modelStore.selectedModel.file,
        requestBody: {
          data: $state.snapshot(modelStore.modelData),
          valves: $state.snapshot(modelStore.modelParams)
        }
      });
      if (id !== requestId) return;
      cloud = result;
      error = '';
    } catch (e) {
      if (id !== requestId) return;
      const detail = (e as { body?: { detail?: unknown } })?.body?.detail;
      error = typeof detail === 'string' ? detail : 'the backend did not return a preview';
    } finally {
      if (id === requestId) loading = false;
    }
  }

  const modelBounds = $derived<Bounds | null>(
    cloud && cloud.x.length
      ? {
          minX: cloud.bounds_min[0]!,
          maxX: cloud.bounds_max[0]!,
          minY: cloud.bounds_min[1]!,
          maxY: cloud.bounds_max[1]!
        }
      : null
  );
  const box = $derived(
    modelBounds && widthPx > 0 ? previewViewBox(modelBounds, widthPx, heightPx) : null
  );

  const blocks = $derived(cloud ? blockInfo(cloud.x, cloud.y, cloud.block) : []);
  const maxBlock = $derived(Math.max(1, ...blocks.map((b) => b.id)));
  const colors = $derived(
    new Map(blocks.map((b) => [b.id, `#${blockIdToColor(b.id / maxBlock).getHexString()}`]))
  );

  // One square per projected point; 3D layers collapse onto the same
  // square, so size from the number of distinct projected positions.
  const cell = $derived.by(() => {
    if (!cloud || !modelBounds || !box) return 0;
    const distinct = new Set(cloud.x.map((x, i) => `${x},${cloud!.y[i]}`)).size;
    const area =
      (modelBounds.maxX - modelBounds.minX) * (modelBounds.maxY - modelBounds.minY) ||
      (box.width * box.height) / 4;
    return Math.sqrt(area / distinct) * 1.15;
  });

  const markers = $derived.by(() => {
    if (!modelBounds) return [];
    const byId = new Map(blocks.map((b) => [b.id, b.bounds]));
    return (modelStore.modelData.boundaryConditions?.conditions ?? []).flatMap((bc) => {
      const bounds = bc.blockId != null ? byId.get(bc.blockId) : undefined;
      const marker = bounds && bcMarker(bc, bounds, modelBounds);
      return marker ? [{ name: bc.name ?? '', marker }] : [];
    });
  });

  // Markers and text are sized in screen pixels (4 px per unit), whatever the model's scale.
  const unit = $derived(box ? 4 * box.px : 1);

  // Block numbers shrink to fit thin blocks (e.g. end grips) instead of overlapping.
  function labelSize(b: Bounds) {
    const blockPx = Math.min(b.maxX - b.minX, b.maxY - b.minY) / box!.px + cell / box!.px;
    return Math.max(2.25, Math.min(3.5, blockPx / 4 / 1.2)) * unit;
  }

  function arrowEnds(m: Extract<Marker, { kind: 'arrow' }>) {
    const gap = unit;
    const len = 8 * unit;
    const [from, to] = m.outward ? [gap, gap + len] : [-(gap + len), -gap];
    return {
      x1: m.x + m.dirX * from,
      y1: -(m.y + m.dirY * from),
      x2: m.x + m.dirX * to,
      y2: -(m.y + m.dirY * to)
    };
  }

  function labelPos(m: Marker) {
    const off = 11 * unit;
    if (m.kind === 'arrow') {
      const along = m.outward ? off : -off;
      return { x: m.x + m.dirX * along, y: -(m.y + m.dirY * along) - (m.dirY ? 0 : 2 * unit) };
    }
    if (m.kind === 'fixed') return { x: m.x + m.outX * off, y: -(m.y + m.outY * off) };
    return { x: m.x, y: -m.y - 4 * unit };
  }
</script>

<div
  class="relative flex h-full w-full flex-col items-center justify-center"
  bind:clientWidth={widthPx}
  bind:clientHeight={heightPx}
>
  {#if ownModel}
    <p class="text-muted-foreground text-sm">
      Uploaded meshes have no preview. Upload the mesh, then open the Model tab to view it.
    </p>
  {:else if cloud && box && cloud.x.length}
    <svg
      viewBox="{box.x} {box.y} {box.width} {box.height}"
      class="absolute inset-0 h-full w-full transition-opacity {loading ? 'opacity-50' : ''}"
      role="img"
      aria-label="Preview of {modelStore.selectedModel
        .file}: {blocks.length} blocks, {markers.length} boundary conditions"
    >
      <defs>
        <marker
          id="preview-arrow"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="4"
          markerHeight="4"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill="currentColor" />
        </marker>
      </defs>

      <g shape-rendering="crispEdges">
        {#each cloud.x as x, i (i)}
          <rect
            x={x - cell / 2}
            y={-cloud.y[i]! - cell / 2}
            width={cell}
            height={cell}
            fill={colors.get(cloud.block[i]!)}
          />
        {/each}
      </g>

      <g
        class="text-foreground"
        fill="none"
        stroke="currentColor"
        stroke-width={0.4 * unit}
        stroke-linecap="round"
      >
        {#each markers as { name, marker } (name + marker.x + marker.y)}
          {#if marker.kind === 'arrow'}
            {@const e = arrowEnds(marker)}
            <line {...e} marker-end="url(#preview-arrow)" />
          {:else if marker.kind === 'fixed'}
            {@const px = marker.outY}
            {@const py = marker.outX}
            {@const cx = marker.x + marker.outX * unit}
            {@const cy = -(marker.y + marker.outY * unit)}
            <line
              x1={cx - px * 4 * unit}
              y1={cy + py * 4 * unit}
              x2={cx + px * 4 * unit}
              y2={cy - py * 4 * unit}
            />
            {#each [-3, -1, 1, 3] as t (t)}
              <line
                x1={cx + px * t * unit}
                y1={cy - py * t * unit}
                x2={cx + px * (t - 1.5) * unit + marker.outX * 2 * unit}
                y2={cy - py * (t - 1.5) * unit - marker.outY * 2 * unit}
              />
            {/each}
          {:else if marker.kind === 'outOfPlane'}
            <circle cx={marker.x} cy={-marker.y} r={2.5 * unit} />
            {#if marker.toward}
              <circle cx={marker.x} cy={-marker.y} r={0.6 * unit} fill="currentColor" />
            {:else}
              <path
                d="M{marker.x - 1.6 * unit},{-marker.y - 1.6 * unit} l{3.2 * unit},{3.2 *
                  unit} m0,{-3.2 * unit} l{-3.2 * unit},{3.2 * unit}"
              />
            {/if}
          {:else}
            <circle cx={marker.x} cy={-marker.y} r={1.5 * unit} />
          {/if}
          {@const l = labelPos(marker)}
          <text
            x={l.x}
            y={l.y}
            fill="currentColor"
            stroke="none"
            font-size={3.2 * unit}
            text-anchor="middle"
            dominant-baseline="middle">{name}</text
          >
        {/each}
      </g>

      <g
        font-weight="700"
        text-anchor="middle"
        dominant-baseline="central"
        fill="white"
        stroke="rgb(0 0 0 / 0.6)"
        stroke-width={0.6 * unit}
        paint-order="stroke"
      >
        {#each blocks as b (b.id)}
          <text x={b.labelX} y={-b.labelY} font-size={labelSize(b.bounds)}>{b.id}</text>
        {/each}
      </g>
    </svg>
  {:else if cloud}
    <p class="text-muted-foreground text-sm">This model has no geometry to preview.</p>
  {:else if !error}
    <p class="text-muted-foreground text-sm">Drawing preview…</p>
  {/if}

  {#if error && !ownModel}
    <p
      class="border-destructive/40 bg-destructive/10 text-destructive absolute top-2 right-2 left-2 rounded-md border px-3 py-1.5 text-xs"
      role="status"
    >
      Preview unavailable: {error}
    </p>
  {/if}
</div>
