<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  // Drawn from the model itself (POST /models/{name}/preview) instead of a
  // hand-made image per model: blocks coloured and numbered, boundary
  // conditions as arrows/supports, and the outlines of the shapes the
  // model is built from. Parameter changes refetch the coarse point cloud
  // (debounced); BC/block edits only redraw. `source` previews unsaved
  // YAML (the /models editor) instead of the saved model file.
  import { previewModel, type ModelData, type PreviewResponse, type Valves } from '$lib/client';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { blockIdToColor } from '$lib/components/three/colorTransfer';
  import {
    bcMarker,
    compileRegion,
    previewMargins,
    previewViewBox,
    shapeOutline,
    type BlockInfo,
    type Bounds,
    type MaskItem,
    type Marker,
    type PreviewShape,
    type Region
  } from '$lib/utils/model-preview';

  let {
    modelName,
    data,
    valves,
    source,
    paused = false
  }: {
    modelName: string;
    data: ModelData;
    valves: Valves;
    source?: string;
    /** Skip fetching, e.g. while config and parameters still belong to the previous model. */
    paused?: boolean;
  } = $props();

  let cloud = $state<PreviewResponse | null>(null);
  let loading = $state(false);
  let error = $state('');
  let requestId = 0;
  let widthPx = $state(0);
  let heightPx = $state(0);

  const uploaded = $derived(data.model.meshSource === 'upload');

  // Only inputs the generator reads trigger a request.
  const geometryKey = $derived(
    JSON.stringify([modelName, valves, data.model, data.discretization, source])
  );

  $effect(() => {
    void geometryKey;
    if (uploaded || paused) return;
    const timer = setTimeout(load, 500);
    return () => clearTimeout(timer);
  });

  async function load() {
    const id = ++requestId;
    loading = true;
    try {
      const result = await previewModel({
        modelName,
        requestBody: {
          data: $state.snapshot(data) as ModelData,
          valves: $state.snapshot(valves) as Valves,
          ...(source !== undefined ? { source } : {})
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

  // Bounds and label anchors come from the full-resolution cloud (backend).
  const blocks = $derived<BlockInfo[]>(
    (cloud?.blocks ?? []).map((b) => ({
      id: b.id,
      bounds: b.bounds as unknown as Bounds,
      labelX: b.labelX,
      labelY: b.labelY
    }))
  );
  const outlines = $derived(
    ((cloud?.shapes ?? []) as unknown as PreviewShape[]).flatMap((shape) => {
      const outline = shapeOutline(shape);
      return outline ? [{ shape, outline }] : [];
    })
  );
  const pointsByBlock = $derived.by(() => {
    const groups = new Map<number, number[]>();
    cloud?.block.forEach((id, i) => {
      if (!groups.has(id)) groups.set(id, []);
      groups.get(id)!.push(i);
    });
    return [...groups];
  });
  // Exact drawing: the body and each block as SVG masks built from the model's primitives and
  // block conditions (support/model/regions.py). Models that make their own point cloud have
  // none and are drawn as points below.
  const uid = Math.random().toString(36).slice(2, 8);
  const regions = $derived.by(() => {
    const r = cloud?.regions as
      { body: Region; blocks: { id: number; region: Region }[] } | null | undefined;
    if (!r || !modelBounds) return null;
    const pad =
      0.05 * Math.max(modelBounds.maxX - modelBounds.minX, modelBounds.maxY - modelBounds.minY) ||
      1;
    const bbox = {
      minX: modelBounds.minX - pad,
      maxX: modelBounds.maxX + pad,
      minY: modelBounds.minY - pad,
      maxY: modelBounds.maxY + pad
    };
    const body = compileRegion(r.body, bbox, `${uid}-body`);
    const blockMasks = r.blocks.map((b, i) => ({
      id: b.id,
      ...compileRegion(b.region, bbox, `${uid}-b${i}`)
    }));
    return {
      rect: {
        x: bbox.minX,
        y: -bbox.maxY,
        width: bbox.maxX - bbox.minX,
        height: bbox.maxY - bbox.minY
      },
      body: body.root,
      blocks: blockMasks,
      masks: [...body.masks, ...blockMasks.flatMap((b) => b.masks)]
    };
  });

  const maxBlock = $derived(
    Math.max(1, ...blocks.map((b) => b.id), ...(regions?.blocks.map((b) => b.id) ?? []))
  );
  const colors = $derived(
    new Map(
      [1, ...blocks.map((b) => b.id), ...(regions?.blocks.map((b) => b.id) ?? [])].map((id) => [
        id,
        `#${blockIdToColor(id / maxBlock).getHexString()}`
      ])
    )
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
    return (data.boundaryConditions?.conditions ?? []).flatMap((bc) => {
      const bounds = bc.blockId != null ? byId.get(bc.blockId) : undefined;
      const marker = bounds && bcMarker(bc, bounds, modelBounds);
      return marker ? [{ name: bc.name ?? '', marker }] : [];
    });
  });

  const box = $derived(
    modelBounds && widthPx > 0
      ? previewViewBox(modelBounds, widthPx, heightPx, previewMargins(markers, modelBounds))
      : null
  );

  const highlight = $derived(viewStore.previewHighlight);
  const DIM = 0.25;
  function blockOpacity(id: number) {
    return highlight?.block == null || highlight.block === id ? 1 : DIM;
  }
  function markerOpacity(name: string) {
    return highlight == null || highlight.bc === name ? 1 : DIM;
  }

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

{#snippet maskItem(item: MaskItem, rect: { x: number; y: number; width: number; height: number })}
  {#if item.kind === 'rect'}
    <rect x={item.x} y={item.y} width={item.width} height={item.height} fill={item.fill} />
  {:else if item.kind === 'ellipse'}
    <ellipse cx={item.cx} cy={item.cy} rx={item.rx} ry={item.ry} fill={item.fill} />
  {:else if item.kind === 'polygon'}
    <polygon points={item.points} fill={item.fill} />
  {:else if item.kind === 'image'}
    <image
      href={item.href}
      x={item.x}
      y={item.y}
      width={item.width}
      height={item.height}
      preserveAspectRatio="none"
    />
  {:else}
    {@render masked(item.masks, item.fill, rect)}
  {/if}
{/snippet}

<!-- "and": the box filled through every mask, nested. -->
{#snippet masked(
  masks: string[],
  fill: string,
  rect: { x: number; y: number; width: number; height: number }
)}
  {#if masks.length}
    <g mask="url(#{masks[0]})">{@render masked(masks.slice(1), fill, rect)}</g>
  {:else}
    <rect {...rect} {fill} />
  {/if}
{/snippet}

<div
  class="relative flex h-full w-full flex-col items-center justify-center"
  bind:clientWidth={widthPx}
  bind:clientHeight={heightPx}
>
  {#if uploaded}
    <p class="text-muted-foreground text-sm">
      Uploaded meshes have no preview here — see the Model tab.
    </p>
  {:else if cloud && box && cloud.x.length}
    <svg
      viewBox="{box.x} {box.y} {box.width} {box.height}"
      class="absolute inset-0 h-full w-full transition-opacity {loading ? 'opacity-50' : ''}"
      role="img"
      aria-label="Preview of {modelName}: {blocks.length} blocks, {markers.length} boundary conditions"
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
        {#if regions}
          {#each regions.masks as mask (mask.id)}
            <mask id={mask.id} maskUnits="userSpaceOnUse" {...regions.rect}>
              {#each mask.items as item, i (i)}
                {@render maskItem(item, regions.rect)}
              {/each}
            </mask>
          {/each}
        {/if}
      </defs>

      {#if regions}
        <!-- Block 1 is the whole body; each block is painted over it through its mask, in
             order, so later blocks win like in the mesh. -->
        <g mask="url(#{regions.body})">
          <rect {...regions.rect} fill={colors.get(1)} opacity={blockOpacity(1)} />
          {#each regions.blocks as block, i (i)}
            <rect
              {...regions.rect}
              fill={colors.get(block.id)}
              mask="url(#{block.root})"
              opacity={blockOpacity(block.id)}
            />
          {/each}
        </g>
      {:else}
        <g shape-rendering="crispEdges">
          <!-- One group per block: opacity on the group composites it as a whole,
             so the overlapping squares don't show seams when dimmed. -->
          {#each pointsByBlock as [id, points] (id)}
            <g fill={colors.get(id)} opacity={blockOpacity(id)}>
              {#each points as i (i)}
                <rect
                  x={cloud.x[i]! - cell / 2}
                  y={-cloud.y[i]! - cell / 2}
                  width={cell}
                  height={cell}
                />
              {/each}
            </g>
          {/each}
        </g>
      {/if}

      <!-- Outlines of the primitives: the body solid, cut-outs dashed, block regions in their colour. -->
      <g fill="none" stroke-width={0.3 * unit} class="text-foreground">
        {#each outlines as { shape, outline }, i (i)}
          {@const stroke =
            shape.role === 'block' ? colors.get(shape.block_id ?? 1) : 'currentColor'}
          {@const dash = shape.role === 'remove' ? `${2 * unit} ${1.5 * unit}` : undefined}
          {@const opacity =
            shape.role === 'block'
              ? blockOpacity(shape.block_id ?? 1)
              : shape.role === 'add'
                ? 0.5
                : 0.8}
          {#if outline.kind === 'rect'}
            <rect
              x={outline.x}
              y={-(outline.y + outline.height)}
              width={outline.width}
              height={outline.height}
              {stroke}
              stroke-dasharray={dash}
              {opacity}
            />
          {:else if outline.kind === 'ellipse'}
            <ellipse
              cx={outline.cx}
              cy={-outline.cy}
              rx={outline.rx}
              ry={outline.ry}
              {stroke}
              stroke-dasharray={dash}
              {opacity}
            />
          {:else}
            <polygon
              points={outline.points.map(([x, y]) => `${x},${-y}`).join(' ')}
              {stroke}
              stroke-dasharray={dash}
              {opacity}
            />
          {/if}
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
          {@const l = labelPos(marker)}
          <g
            opacity={markerOpacity(name)}
            stroke-width={highlight?.bc === name ? 0.8 * unit : undefined}
            class="transition-opacity"
          >
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
            <text
              x={l.x}
              y={l.y}
              fill="currentColor"
              stroke="none"
              font-size={3.2 * unit}
              text-anchor="middle"
              dominant-baseline="middle">{name}</text
            >
          </g>
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
          <text
            x={b.labelX}
            y={-b.labelY}
            font-size={labelSize(b.bounds)}
            opacity={blockOpacity(b.id)}>{b.id}</text
          >
        {/each}
      </g>
    </svg>
  {:else if cloud}
    <p class="text-muted-foreground text-sm">This model has no geometry to preview.</p>
  {:else if !error}
    <p class="text-muted-foreground text-sm">Drawing preview…</p>
  {/if}

  {#if error && !uploaded}
    <p
      class="border-destructive/40 bg-destructive/10 text-destructive absolute top-2 right-2 left-2 rounded-md border px-3 py-1.5 text-xs"
      role="status"
    >
      Preview unavailable: {error}
    </p>
  {/if}
</div>
