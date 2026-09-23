<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  let { sourceFile }: { sourceFile: string } = $props();
</script>

<div class="flex h-full items-center justify-center p-6">
  <div class="max-w-md rounded-md border border-dashed border-border bg-muted/50 p-4 text-sm text-muted-foreground">
    <p class="font-medium text-foreground">Not yet ported to Svelte</p>
    <p class="mt-1">
      This 3D/VTK-based view still needs to be migrated from
      <code class="rounded bg-muted px-1 py-0.5 font-mono text-xs">{sourceFile}</code>. It should
      wrap <code class="rounded bg-muted px-1 py-0.5 font-mono text-xs">vtk.js</code> the same way
      <code class="rounded bg-muted px-1 py-0.5 font-mono text-xs">PlotlyChart.svelte</code>
      wraps plotly.js — initialise on mount, update in an <code class="rounded bg-muted px-1 py-0.5 font-mono text-xs"
        >$effect</code
      >, tear down `onDestroy`. See MIGRATION.md for the full checklist.
    </p>
  </div>
</div>
