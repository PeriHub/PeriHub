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
  import { initAuth } from '$lib/auth/oauth';
  import { loadPublicConfig } from '$lib/config';
  import { refreshModelFromBackend, modelNeedsRefresh } from '$lib/utils/modelSync';

  let { children } = $props();

  // The /perihub tool page is a dense, single-screen working area - it
  // manages its own fixed-height layout and doesn't want the footer eating
  // into that budget or the page becoming scrollable as a whole. Every
  // other route keeps the normal document flow with the footer.
  const isFullScreenTool = $derived($page.url.pathname === '/perihub');

  function resetData() {
    refreshModelFromBackend(modelStore.selectedModel.file);
  }

  // Both auth-flow pages drive their own login (exchange -> token ->
  // initAuth()) before navigating away - the OAuth callback page
  // (routes/auth/callback) and the local email/password page
  // (routes/auth/login). If this layout's onMount also called initAuth()
  // on either route, it would kick off a second, redundant login
  // redirect/fetch and race the page's own handling. So skip it on both
  // and let each page drive auth setup for its one render.
  const skipsOwnInitAuth = ['/auth/callback', '/auth/login'].includes($page.url.pathname);

  onMount(() => {
    (async () => {
      // Populate publicConfig (trial/cluster/oauth flags) before anything
      // that reads it - defaultStore.initialiseStore() reads publicConfig.trial,
      // and initAuth() below decides its whole flow from publicConfig.oauthEnabled.
      await loadPublicConfig();

      defaultStore.initialiseStore();
      modelStore.initialiseStore();
      document.documentElement.classList.toggle('dark', defaultStore.darkMode);

      if (!skipsOwnInitAuth) {
        await initAuth();
      }

      // Load the selected model's config/valves automatically instead of
      // requiring a manual "Reset Data" click - but only when there's
      // nothing usable cached yet (first visit, or localStorage's
      // selectedModel and modelData/modelParams belong to different models
      // after drifting apart between sessions). If they already match, the
      // cache is left alone so in-progress edits survive a reload.
      if (modelNeedsRefresh(modelStore.selectedModel.file)) {
        resetData();
      }
    })();

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
