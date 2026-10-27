<!--
  The form of one PeriLab section entry, generated from the PeriLab schema (src/lib/perilab): every key the current
  selection offers, required keys and required groups ("one of ...") first, then "Optional", each in PeriLab's
  declaration order. Values live in
  `values` (the entry's `params`, YAML key -> value); the backend writer merges them into the deck. Keys an
  expansion renders itself are passed as `custom`.
-->
<script lang="ts">
  import { Trash2, TriangleAlert } from 'lucide-svelte';
  import {
    coerce,
    enumOf,
    groupLabel,
    groupUnmet,
    isSet,
    paramsFor,
    pick,
    propInfo,
    widgetOf,
    type SchemaProp
  } from '$lib/perilab/schema';
  import InfoTip from '$lib/components/ui/InfoTip.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from './SchemaParams.svelte';

  interface Props {
    entry: SchemaProp | undefined;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    values: Record<string, any>;
    names?: readonly string[];
    custom?: readonly string[];
    solver?: string;
    idPrefix: string;
    /** Placeholder per key instead of PeriLab's default, e.g. a calculated elastic constant. */
    hints?: Record<string, string | undefined>;
  }

  let { entry, values, names = [], custom = [], solver, idPrefix, hints = {} }: Props = $props();

  const offered = $derived(paramsFor(entry, names, custom, { values, solver }));
  const keys = $derived(Object.keys(offered.props));
  const inGroup = (key: string) => offered.groups.some((g) => g.keys.includes(key));
  const required = $derived(keys.filter((key) => offered.required.has(key) || inGroup(key)));
  const optional = $derived(keys.filter((key) => !offered.required.has(key) && !inGroup(key)));
  // Set earlier but not offered by the current selection (other model/solver/Type, or dropped by PeriLab): still
  // written to the deck, so show it rather than let PeriLab warn about a key the user can't see.
  const leftovers = $derived(
    Object.keys(values).filter((key) => !(key in offered.props) && !custom.includes(key))
  );

  function set(key: string, value: unknown) {
    if (value === undefined) delete values[key];
    else values[key] = value;
  }

  const id = (key: string) => `${idPrefix}-pl-${key.replace(/\W+/g, '-')}`;
  const placeholder = (key: string, prop: SchemaProp) =>
    hints[key] ?? (prop.default != null ? `Default ${String(prop.default)}` : 'Not set');
  const missing = (key: string) =>
    !isSet(values[key]) &&
    (offered.required.has(key) ||
      offered.groups.some((g) => g.keys.includes(key) && groupUnmet(g, values)));
</script>

{#snippet field(key: string, prop: SchemaProp)}
  {@const widget = widgetOf(prop)}
  {@const about = propInfo(prop)}
  {@const descId = about.text || about.facts.length ? `${id(key)}-desc` : undefined}
  {@const isRequired = offered.required.has(key)}
  {#if prop.type === 'object' && prop.properties}
    <fieldset class="border-border basis-full space-y-2 rounded-md border px-3 py-2">
      <div class="flex items-center gap-1.5">
        <Toggle
          id={id(key)}
          checked={values[key] != null}
          onCheckedChange={(on: boolean) => set(key, on ? {} : undefined)}
          label={key}
        />
        {#if descId}<InfoTip title={key} text={about.text} facts={about.facts} id={descId} />{/if}
      </div>
      {#if values[key] != null}
        <SchemaParams entry={prop} values={values[key]} idPrefix={id(key)} />
      {/if}
    </fieldset>
  {:else if widget === 'toggle'}
    <div class="flex items-center gap-1.5">
      <Toggle
        id={id(key)}
        checked={(values[key] ?? prop.default ?? false) as boolean}
        onCheckedChange={(v: boolean) => set(key, v)}
        label={isRequired ? `${key} *` : key}
        required={isRequired}
      />
      {#if descId}<InfoTip title={key} text={about.text} facts={about.facts} id={descId} />{/if}
    </div>
  {:else}
    <div class="space-y-1">
      <ParamLabel {key} {prop} for={id(key)} required={isRequired} {descId} />
      {#if widget === 'select'}
        <Select
          id={id(key)}
          class={missing(key) ? 'border-destructive' : ''}
          aria-describedby={descId}
          aria-required={isRequired}
          aria-invalid={missing(key)}
          value={(values[key] ?? '') as string}
          onchange={(e: Event) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            set(key, v === '' ? undefined : v);
          }}
        >
          <option value="">{placeholder(key, prop)}</option>
          {#each pick(enumOf(prop), [], values[key] as string | undefined) as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </Select>
      {:else}
        <Input
          id={id(key)}
          class={missing(key) ? 'border-destructive' : ''}
          aria-describedby={descId}
          aria-required={isRequired}
          aria-invalid={missing(key)}
          type={widget === 'number' ? 'number' : 'text'}
          step={widget === 'number' ? 'any' : undefined}
          min={prop.minimum}
          max={prop.maximum}
          placeholder={placeholder(key, prop)}
          value={(values[key] ?? '') as string}
          onchange={(e: Event) =>
            set(key, coerce(prop, (e.currentTarget as HTMLInputElement).value))}
        />
      {/if}
      {#if missing(key) && isRequired}<p class="text-destructive text-xs">Required</p>{/if}
    </div>
  {/if}
{/snippet}

{#if required.length}
  <div class="flex flex-wrap items-start gap-3">
    {#each required as key (key)}{@render field(key, offered.props[key]!)}{/each}
  </div>
{/if}
{#each offered.groups as group (group.keys.join())}
  <p class="text-xs {groupUnmet(group, values) ? 'text-destructive' : 'text-muted-foreground'}">
    Give {groupLabel(group)}{group.max == null ? '' : ` (at most ${group.max})`}
  </p>
{/each}
{#if optional.length}
  <p class="text-muted-foreground pt-1 text-xs font-medium tracking-wide uppercase">Optional</p>
  <div class="flex flex-wrap items-start gap-3">
    {#each optional as key (key)}{@render field(key, offered.props[key]!)}{/each}
  </div>
{/if}
{#each leftovers as key (key)}
  <div class="text-muted-foreground flex items-center gap-2 pt-2 text-xs">
    <TriangleAlert class="h-3.5 w-3.5" aria-hidden="true" />
    <span
      >{key} = {JSON.stringify(values[key])} is not a parameter of the current PeriLab selection</span
    >
    <Button variant="ghost" size="icon" onclick={() => set(key, undefined)} title="Remove {key}">
      <Trash2 class="h-4 w-4" />
    </Button>
  </div>
{/each}
