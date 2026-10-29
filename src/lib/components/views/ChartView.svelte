<script lang="ts">
  import { LoaderCircle } from 'lucide-svelte';
  import SeriesLineChart, { PALETTE } from '$lib/components/views/SeriesLineChart.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import { getPlot } from '$lib/client';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { notify } from '$lib/utils/notify';

  const modelData = $derived(modelStore.modelData);
  // Only CSV outputs hold the global values plotted here.
  const csvOutputs = $derived(
    (modelData.outputs ?? []).filter((o) => (o.params?.['Output File Type'] ?? 'Exodus') === 'CSV')
  );
  let output = $state('');
  const outputName = $derived(
    csvOutputs.some((o) => o.name === output) ? output : (csvOutputs[0]?.name ?? '')
  );

  // The run's CSV by column; any column can be the x axis (e.g. a force-displacement curve).
  let columns = $state.raw(new Map<string, number[]>());
  let loading = $state(false);

  // Loaded whenever the tab is shown, so a rerun's CSV is picked up.
  $effect(() => {
    if (viewStore.viewId !== 'plotly' || !outputName) return;
    load(outputName, defaultStore.status.run_id ?? null);
  });

  async function load(name: string, runId: string | null) {
    loading = true;
    try {
      const data = (await getPlot({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        output: name,
        deviationsEnabled: modelData.deviations?.enabled ?? false,
        runId
      })) as Record<string, (number | string)[]>;
      // CSV cells can arrive as strings; an axis needs real numbers ("10" < "9" as strings).
      columns = new Map(Object.entries(data).map(([key, values]) => [key, values.map(Number)]));
    } catch (error) {
      notify.apiError(error);
    }
    loading = false;
  }

  const names = $derived([...columns.keys()]);

  // CSV columns differ by orders of magnitude (forces ~1e-1 next to
  // displacements ~1e-6) and share one y axis, so a new plot starts with a
  // single y column and more are toggled in.
  let xName = $state('');
  let yNames = $state<string[]>([]);
  $effect(() => {
    xName = names[0] ?? '';
    yNames = names.slice(1, 2);
  });

  // Fixed per column, so a curve keeps its color while others are toggled; the toggles double as the legend.
  const colorOf = (name: string) => PALETTE[names.indexOf(name) % PALETTE.length]!;

  function toggleY(name: string) {
    yNames = yNames.includes(name) ? yNames.filter((n) => n !== name) : [...yNames, name];
  }

  const series = $derived(
    yNames
      .filter((name) => name !== xName)
      .map((name) => ({
        name,
        x: columns.get(xName) ?? [],
        y: columns.get(name) ?? [],
        color: colorOf(name)
      }))
  );
</script>

<div class="relative flex h-full flex-col gap-2 p-2">
  <div class="flex flex-wrap items-center gap-2 text-xs">
    {#if csvOutputs.length > 1}
      <Label for="chart-output">Output</Label>
      <Select
        id="chart-output"
        value={outputName}
        onchange={(e) => (output = e.currentTarget.value)}
        class="w-auto"
      >
        {#each csvOutputs as o, i (i)}
          <option value={o.name}>{o.name}</option>
        {/each}
      </Select>
    {/if}
    <Label for="chart-x">X</Label>
    <Select id="chart-x" bind:value={xName} class="w-auto">
      {#each names as name (name)}
        <option value={name}>{name}</option>
      {/each}
    </Select>
    <span class="text-muted-foreground ml-2">Y</span>
    {#each names.filter((n) => n !== xName) as name (name)}
      <button
        type="button"
        onclick={() => toggleY(name)}
        aria-pressed={yNames.includes(name)}
        style:border-color={yNames.includes(name) ? colorOf(name) : undefined}
        class="border-border hover:bg-muted flex items-center gap-1.5 rounded-full border px-2 py-0.5 {yNames.includes(
          name
        )
          ? 'text-foreground'
          : 'text-muted-foreground'}"
      >
        <span
          class="h-2 w-2 rounded-full"
          style:background={yNames.includes(name) ? colorOf(name) : 'transparent'}
        ></span>
        {name}
      </button>
    {/each}
  </div>
  <SeriesLineChart
    {series}
    xLabel={xName}
    yLabel={yNames.length === 1 ? yNames[0] : ''}
    legend={false}
    class="min-h-0 flex-1"
  />
  {#if loading}
    <div class="bg-background/40 absolute inset-0 flex items-center justify-center">
      <LoaderCircle class="text-primary h-10 w-10 animate-spin" />
    </div>
  {/if}
</div>
