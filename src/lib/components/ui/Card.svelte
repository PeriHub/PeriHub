<script lang="ts">
  import { cn } from '$lib/utils';

  let {
    class: className,
    children,
    ...rest
  }: { class?: string; children?: import('svelte').Snippet } & Record<string, unknown> = $props();
</script>

<div
  class={cn('border-border bg-card text-card-foreground rounded-xl border shadow-sm', className)}
  {...rest}
>
  {@render children?.()}
</div>
