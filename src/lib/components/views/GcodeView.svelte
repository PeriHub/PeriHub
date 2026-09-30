<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!-- Toolpath preview of an uploaded G-code mesh, after
     https://github.com/xyz-tools/gcode-preview-svelte. Loaded with a dynamic
     import() by ModelView, since gcode-preview brings its own three.js copy. -->
<script lang="ts">
  import { GCodePreview } from 'gcode-preview';
  import { api } from '$lib/api/client';

  let {
    modelName,
    folderName,
    filename
  }: { modelName: string; folderName: string; filename: string } = $props();

  let canvas: HTMLCanvasElement;
  let preview: GCodePreview | undefined;
  // Identifies the most recent load, so a request that resolves late can bail out.
  let loadId = 0;
  let loading = $state(false);
  let error = $state('');

  // No reactive reads: set the preview up once, tear it down on unmount.
  $effect(() => {
    preview = new GCodePreview({ canvas, extrusionColor: 'hotpink' });
    const observer = new ResizeObserver(() => preview?.sceneManager.resize());
    observer.observe(canvas);
    return () => {
      observer.disconnect();
      loadId++;
      preview?.dispose();
      preview = undefined;
    };
  });

  $effect(() => {
    load(
      `/workspaces/${encodeURIComponent(modelName)}/${encodeURIComponent(folderName)}/files/${encodeURIComponent(filename)}`
    );
  });

  async function load(url: string) {
    if (!preview) return;
    const id = ++loadId;
    preview.clear();
    loading = true;
    error = '';
    try {
      const response = await api.get<string>(url, { responseType: 'text' });
      if (id !== loadId) return;
      await preview.processGCodeStream(response.data);
      if (id === loadId) loading = false;
    } catch (cause) {
      if (id !== loadId) return;
      loading = false;
      error = `Can't preview ${filename}: ${cause instanceof Error ? cause.message : String(cause)}`;
    }
  }
</script>

<div class="relative h-full w-full">
  <canvas
    bind:this={canvas}
    class="h-full w-full cursor-grab"
    aria-label="G-code preview of {filename}"
  ></canvas>
  <p role="status" class="text-muted-foreground absolute top-2 left-2 text-xs">
    {loading ? 'Loading G-code…' : ''}
  </p>
  <p role="alert" class="text-destructive absolute top-2 left-2 text-sm">{error}</p>
</div>
