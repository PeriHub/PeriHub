<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  Landing-page hero: replays a real PeriLab result (Kalthoff–Winkler), drawn
  the way ResultsView draws it - points displaced by a displacement factor
  and coloured by displacement magnitude on the same colour scale. The data
  is a thinned-out export made by scripts/export_hero_result.py.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import { Pause, Play } from 'lucide-svelte';
  import { valueToColor } from '$lib/components/three/colorTransfer';

  type HeroResult = {
    model: string;
    dx: number;
    x0: number;
    y0: number;
    steps: number[];
    number_of_steps: number;
    times: number[];
    u_scale: number;
    u_max: number;
    displ_factor: number;
    idx: string;
    u: string;
  };

  const FRAME_MS = 150;
  const PAD = 12;
  const BINS = 64;
  // same scale ResultsView uses, sampled into bins so each frame needs only
  // BINS fillStyle changes
  const PALETTE = Array.from(
    { length: BINS },
    (_, i) => `#${valueToColor(i / (BINS - 1), 0, 1).getHexString()}`
  );

  let canvas = $state<HTMLCanvasElement>();
  let wrap = $state<HTMLElement>();
  let data = $state<HeroResult | null>(null);
  let failed = $state(false);
  let frame = $state(0);
  let playing = $state(false);
  let bounds = $state({ x0: 0, x1: 1, y0: 0, y1: 2 });

  // decoded arrays, positions in model units
  let px: Float32Array;
  let py: Float32Array;
  let u: Int8Array;
  let timer: ReturnType<typeof setInterval> | undefined;

  const bytes = (b64: string) => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)).buffer;
  const frames = $derived(data?.steps.length ?? 1);
  const aspect = $derived((bounds.x1 - bounds.x0) / (bounds.y1 - bounds.y0));

  function decode(d: HeroResult) {
    const idx = new Int16Array(bytes(d.idx));
    u = new Int8Array(bytes(d.u));
    const n = idx.length / 2;
    px = new Float32Array(n);
    py = new Float32Array(n);
    for (let k = 0; k < n; k++) {
      px[k] = d.x0 + idx[2 * k] * d.dx;
      py[k] = d.y0 + idx[2 * k + 1] * d.dx;
    }
    // fit the deformed shape of every frame, not just the undeformed plate
    const s = d.u_scale * d.displ_factor;
    let [x0, x1, y0, y1] = [Infinity, -Infinity, Infinity, -Infinity];
    for (let f = 0; f < d.steps.length; f++) {
      for (let k = 0; k < n; k++) {
        const x = px[k] + u[2 * (f * n + k)] * s;
        const y = py[k] + u[2 * (f * n + k) + 1] * s;
        x0 = Math.min(x0, x);
        x1 = Math.max(x1, x);
        y0 = Math.min(y0, y);
        y1 = Math.max(y1, y);
      }
    }
    bounds = { x0, x1, y0, y1 };
  }

  function draw() {
    const ctx = canvas?.getContext('2d');
    if (!ctx || !data || !canvas) return;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    const bw = bounds.x1 - bounds.x0;
    const bh = bounds.y1 - bounds.y0;
    const scale = Math.min((w - 2 * PAD) / bw, (h - 2 * PAD) / bh);
    const ox = (w - bw * scale) / 2;
    const oy = (h - bh * scale) / 2;
    const size = Math.max(1, 2 * data.dx * scale);
    const n = px.length;
    const s = data.u_scale;
    const bins: number[][] = PALETTE.map(() => []);
    for (let k = 0; k < n; k++) {
      const m = Math.hypot(u[2 * (frame * n + k)], u[2 * (frame * n + k) + 1]) * s;
      bins[Math.min(BINS - 1, Math.floor((m / data.u_max) * BINS))].push(k);
    }
    const f = s * data.displ_factor;
    bins.forEach((list, b) => {
      ctx.fillStyle = PALETTE[b];
      for (const k of list) {
        const x = px[k] + u[2 * (frame * n + k)] * f;
        const y = py[k] + u[2 * (frame * n + k) + 1] * f;
        // flip y: model y points up, canvas y points down
        ctx.fillRect(
          ox + (x - bounds.x0) * scale - size / 2,
          oy + (bounds.y1 - y) * scale - size / 2,
          size,
          size
        );
      }
    });
  }

  function pause() {
    playing = false;
    clearInterval(timer);
  }

  function play() {
    if (frame >= frames - 1) frame = 0;
    playing = true;
    clearInterval(timer);
    timer = setInterval(() => {
      if (frame < frames - 1) frame += 1;
      else pause();
    }, FRAME_MS);
  }

  $effect(() => {
    void frame;
    void aspect;
    draw();
  });

  onMount(() => {
    const ro = new ResizeObserver(() => draw());
    fetch('/hero/kalthoff-winkler.json')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((d: HeroResult) => {
        decode(d);
        data = d;
        if (wrap) ro.observe(wrap);
        if (matchMedia('(prefers-reduced-motion: reduce)').matches) frame = d.steps.length - 1;
        else play();
      })
      .catch(() => (failed = true));
    return () => {
      ro.disconnect();
      clearInterval(timer);
    };
  });
</script>

<figure class="overflow-hidden rounded-xl bg-[#0B3A4A] text-[#CFE3EA]">
  <div
    bind:this={wrap}
    class="relative mx-auto h-[60vh] max-w-full lg:h-[520px]"
    style:aspect-ratio={aspect}
  >
    <canvas bind:this={canvas} class="block h-full w-full">
      Kalthoff–Winkler plate: a PeriLab result of an impact on the left edge, points coloured by
      displacement magnitude.
    </canvas>
    {#if failed}
      <p class="absolute inset-0 grid place-items-center p-4 text-center font-mono text-xs">
        Result preview unavailable
      </p>
    {/if}
  </div>

  {#if !failed}
    <figcaption class="space-y-2 border-t border-white/10 px-4 py-3 font-mono text-xs">
      {#if data}
        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={playing ? pause : play}
            aria-label={playing ? 'Pause' : 'Play'}
            class="rounded p-1 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-[#D2AE3D]"
          >
            {#if playing}<Pause class="size-4" />{:else}<Play class="size-4" />{/if}
          </button>
          <input
            type="range"
            min="0"
            max={frames - 1}
            bind:value={frame}
            oninput={pause}
            aria-label="Time step"
            class="flex-1 accent-[#D2AE3D]"
          />
        </div>
        <div class="flex justify-between tabular-nums">
          <span>step {data.steps[frame]} / {data.number_of_steps}</span>
          <span>t = {data.times[frame].toExponential(2)}</span>
        </div>
        <p class="text-white/60">{data.model} · PeriLab result</p>
      {:else}
        <p class="text-white/60">Loading result…</p>
      {/if}
    </figcaption>
  {/if}
</figure>
