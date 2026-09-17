<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  let { title, children }: { title: string; children?: import('svelte').Snippet } = $props();
</script>

<svelte:head>
  <title>{title} — PeriHub</title>
</svelte:head>

<article class="legal-page mx-auto max-w-3xl px-6 py-16">
  <h1 class="mb-6 text-2xl font-semibold tracking-tight">{title}</h1>
  <div class="space-y-3 text-sm leading-relaxed text-foreground/90">
    {@render children?.()}
  </div>
</article>

<style>
  .legal-page :global(a) {
    color: var(--primary);
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  .legal-page :global(b) {
    font-weight: 600;
  }
</style>
