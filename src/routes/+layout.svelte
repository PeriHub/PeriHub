<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
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

<div class="flex min-h-screen flex-col">
  <Header />
  <main class="flex-1">
    {@render children?.()}
  </main>
  <Footer />
</div>

<Toaster richColors position="bottom-right" duration={2500} />
