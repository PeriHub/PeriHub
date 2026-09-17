<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { cn } from '$lib/utils';

  let {
    class: className,
    children,
    ...rest
  }: { class?: string; children?: import('svelte').Snippet } & Record<string, unknown> = $props();
</script>

<div
  class={cn('rounded-xl border border-border bg-card text-card-foreground shadow-sm', className)}
  {...rest}
>
  {@render children?.()}
</div>
