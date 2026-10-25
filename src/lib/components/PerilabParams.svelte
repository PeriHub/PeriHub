<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  PeriLab parameters PeriHub has no own field for, generated from the PeriLab schema (src/lib/perilab). Values
  live in owner[field] (YAML key -> value); the backend writer merges them into the deck and native fields win.
-->
<script lang="ts">
  import { Trash2, TriangleAlert } from 'lucide-svelte';
  import { coerce, enumOf, widgetOf, type SchemaProp } from '$lib/perilab/schema';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  interface Props {
    params: Record<string, SchemaProp>;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    owner: Record<string, any>;
    field?: string;
    idPrefix: string;
    title?: string;
  }

  let {
    params,
    owner,
    field = 'extra',
    idPrefix,
    title = 'Additional PeriLab parameters'
  }: Props = $props();

  const values = $derived((owner[field] ?? {}) as Record<string, unknown>);
  // Set earlier but no longer offered (PeriLab dropped it, or another model/solver type was picked):
  // still written to the deck, so show it rather than let PeriLab reject a key the user can't see.
  const unknownKeys = $derived(Object.keys(values).filter((key) => !(key in params)));
  const count = $derived(Object.keys(params).length);

  function set(key: string, value: unknown) {
    if (value === undefined) {
      if (owner[field]) delete owner[field][key];
      return;
    }
    owner[field] ??= {};
    owner[field][key] = value;
  }

  const id = (key: string) => `${idPrefix}-pl-${key.replace(/\W+/g, '-')}`;
  const hint = (prop: SchemaProp) => (prop.default != null ? String(prop.default) : undefined);
</script>

{#if count > 0 || unknownKeys.length > 0}
  <details class="border-border rounded-md border px-3 py-2">
    <summary class="cursor-pointer text-sm">{title} ({count})</summary>
    <div class="flex flex-wrap items-end gap-3 pt-3">
      {#each Object.entries(params) as [key, prop] (key)}
        {@const widget = widgetOf(prop)}
        <div class="space-y-1" title={prop.description}>
          {#if widget === 'toggle'}
            <Toggle
              id={id(key)}
              checked={(values[key] ?? prop.default ?? false) as boolean}
              onCheckedChange={(v: boolean) => set(key, v)}
              label={key}
            />
          {:else}
            <Label for={id(key)}>{key}</Label>
            {#if widget === 'select'}
              <Select
                id={id(key)}
                value={(values[key] ?? '') as string}
                onchange={(e: Event) => {
                  const v = (e.currentTarget as HTMLSelectElement).value;
                  set(key, v === '' ? undefined : v);
                }}
              >
                <option value="">{hint(prop) ? `Default (${hint(prop)})` : 'Not set'}</option>
                {#each enumOf(prop) as option (option)}
                  <option value={option}>{option}</option>
                {/each}
              </Select>
            {:else}
              <Input
                id={id(key)}
                type={widget === 'number' ? 'number' : 'text'}
                step={widget === 'number' ? 'any' : undefined}
                min={prop.minimum}
                max={prop.maximum}
                placeholder={hint(prop)}
                value={(values[key] ?? '') as string}
                onchange={(e: Event) =>
                  set(key, coerce(prop, (e.currentTarget as HTMLInputElement).value))}
              />
            {/if}
          {/if}
        </div>
      {/each}
    </div>
    {#each unknownKeys as key (key)}
      <div class="text-muted-foreground flex items-center gap-2 pt-2 text-xs">
        <TriangleAlert class="h-3.5 w-3.5" aria-hidden="true" />
        <span
          >{key} = {String(values[key])} is not a parameter of the current PeriLab selection</span
        >
        <Button
          variant="ghost"
          size="icon"
          onclick={() => set(key, undefined)}
          title="Remove {key}"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    {/each}
  </details>
{/if}
