<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import mediumZoom from 'medium-zoom';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { config } from '$lib/config';

  let img: HTMLImageElement;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let zoom: any;

  onMount(() => {
    zoom = mediumZoom(img, { margin: 24 });
  });

  onDestroy(() => zoom?.detach());

  function showModelImg(modelName: string) {
    viewStore.modelImg = `${config.apiBase}/assets/images/${modelName}.jpg`;
    viewStore.viewId = 'image';
  }

  onMount(() => {
    bus.on('showModelImg', showModelImg);
    return () => bus.off('showModelImg', showModelImg);
  });
</script>

<div class="flex h-full w-full items-center justify-center p-2">
  <img bind:this={img} src={viewStore.modelImg} alt="Model" class="max-h-full max-w-full cursor-zoom-in" />
</div>
