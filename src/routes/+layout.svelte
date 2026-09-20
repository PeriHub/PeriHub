<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { Toaster } from 'svelte-sonner';
  import Header from '$lib/components/layout/Header.svelte';
  import Footer from '$lib/components/layout/Footer.svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { initAuth } from '$lib/auth/keycloak';
  import { getValves, getConfig } from '$lib/client';
  import type { ModelData } from '$lib/client';

  let { children } = $props();

  // The /perihub tool page is a dense, single-screen working area - it
  // manages its own fixed-height layout and doesn't want the footer eating
  // into that budget or the page becoming scrollable as a whole. Every
  // other route keeps the normal document flow with the footer.
  const isFullScreenTool = $derived($page.url.pathname === '/perihub');

  function resetData() {
    getConfig({ configFile: modelStore.selectedModel.file })
      .then((response) => {
        const data = JSON.parse(JSON.stringify(response));
        modelStore.modelData = { ...modelStore.modelData, ...data } as ModelData;
      })
      .catch((error) => notify.apiError(error));

    getValves({ modelName: modelStore.selectedModel.file })
      .then((response) => {
        modelStore.modelParams = structuredClone(response);
      })
      .catch((error) => notify.apiError(error));
  }

  onMount(() => {
    defaultStore.initialiseStore();
    modelStore.initialiseStore();
    document.documentElement.classList.toggle('dark', defaultStore.darkMode);

    initAuth();

    bus.on('resetData', resetData);
    return () => bus.off('resetData', resetData);
  });
</script>

<div class="flex flex-col {isFullScreenTool ? 'h-screen overflow-hidden' : 'min-h-screen'}">
  <Header />
  <main class="flex-1 {isFullScreenTool ? 'min-h-0 overflow-hidden' : ''}">
    {@render children?.()}
  </main>
  {#if !isFullScreenTool}
    <Footer />
  {/if}
</div>

<Toaster richColors position="bottom-right" duration={2500} />
