<script lang="ts">
  import { cn } from '$lib/utils';

  let {
    class: className,
    children,
    ...rest
  }: { class?: string; children?: import('svelte').Snippet } & Record<string, unknown> = $props();
</script>

<label class={cn('text-sm leading-none font-medium', className)} {...rest}>
  {@render children?.()}
</label>
