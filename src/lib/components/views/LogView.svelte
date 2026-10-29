<script lang="ts">
  import { tick } from 'svelte';
  import { LoaderCircle, TriangleAlert } from 'lucide-svelte';
  import CodeBlock from '$lib/components/views/CodeBlock.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';

  const hasLog = $derived(viewStore.logOutput.trim().length > 0);

  // Follows new log lines while scrolled to the bottom; scrolling up pauses that until scrolled back down.
  // The log's own <pre> (CodeBlock) is what scrolls - it is sized to this panel.
  let panel: HTMLDivElement | undefined = $state();
  let follow = true;

  // Scroll events don't bubble, hence onscrollcapture on the panel.
  function onScroll(event: Event) {
    const el = event.target as HTMLElement;
    follow = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
  }

  $effect(() => {
    void viewStore.logOutput;
    // A hidden tab can't scroll, so also catch up when the Log tab is shown.
    if (viewStore.textId !== 'log' || !follow || !panel) return;
    tick().then(() => {
      const log = panel?.querySelector('pre');
      log?.scrollTo({ top: log.scrollHeight });
    });
  });
</script>

<div class="flex h-full flex-col overflow-y-auto" bind:this={panel} onscrollcapture={onScroll}>
  {#if viewStore.logStatus === 'waiting' && !hasLog}
    <div class="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-center">
      <LoaderCircle class="text-primary h-10 w-10 animate-spin" />
      <p class="text-muted-foreground text-sm">{viewStore.logStatusMessage}</p>
    </div>
  {:else if viewStore.logStatus === 'idle' && !hasLog}
    <div class="flex flex-1 items-center justify-center p-6 text-center">
      <p class="text-muted-foreground text-sm">
        No job is currently running for this model. Submit it to see its log here.
      </p>
    </div>
  {:else}
    {#if viewStore.logStatus === 'waiting'}
      <div class="border-border bg-muted/40 flex items-center gap-2 border-b px-3 py-1.5">
        <LoaderCircle class="text-primary h-3.5 w-3.5 animate-spin" />
        <p class="text-muted-foreground text-xs">{viewStore.logStatusMessage}</p>
      </div>
    {:else if viewStore.logStatus === 'error'}
      <div class="border-border bg-destructive/10 flex items-center gap-2 border-b px-3 py-1.5">
        <TriangleAlert class="text-destructive h-3.5 w-3.5 shrink-0" />
        <p class="text-destructive text-xs">{viewStore.logStatusMessage}</p>
      </div>
    {/if}
    <CodeBlock bind:value={viewStore.logOutput} editable={false} class="min-h-full flex-1" />
  {/if}
</div>
