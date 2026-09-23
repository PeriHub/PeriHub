<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts" module>
  // Everything this component needs, read directly off the generated OpenAPI
  // schema. These are emitted by the backend's yaml_field() helper (see
  // backend/app/support/yaml_field.py) as sibling keys next to the normal
  // JSON Schema `type`/`title`, so they survive `npm run client` untouched -
  // there's no separate frontend config file to keep in sync.
  interface SchemaProperty {
    ui_label?: string;
    ui_widget?: 'text' | 'number' | 'toggle' | 'select' | 'hidden';
    ui_group?: string;
    ui_order?: number;
    ui_options?: string[];
    [key: string]: unknown;
  }

  interface SchemaLike {
    properties?: Record<string, SchemaProperty>;
  }
</script>

<script lang="ts">
  import * as schemas from '$lib/client/schemas.gen';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Label from '$lib/components/ui/Label.svelte';

  interface Props {
    /** Name of the Pydantic model, e.g. "Job" or "Solver" - looked up as `$<schemaName>` in schemas.gen.ts. */
    schemaName: string;
    /** The bound data object (e.g. `job`, `solver`) - fields are read/written directly by name. */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    data: Record<string, any>;
    /**
     * Only render fields whose `ui_group` matches this value. Lets one model
     * feed more than one visual section - e.g. Solver's plain fields
     * (ui_group: "Solver") render separately from its Verlet-only fields
     * (ui_group: "Verlet"), which only make sense to show once the user has
     * picked that solver type.
     */
    group?: string;
    /** Extra callback fired after any field in this form changes, for components that need to react (e.g. re-deriving a value). */
    onchange?: () => void;
    /** Field names to render disabled (e.g. trial-mode restrictions) - a real per-instance UX concern, so it's passed in rather than inferred from the schema. */
    disabledFields?: string[];
  }

  let { schemaName, data, group, onchange, disabledFields = [] }: Props = $props();

  function getSchema(name: string): SchemaLike | undefined {
    const key = `$${name}` as keyof typeof schemas;
    return schemas[key] as unknown as SchemaLike | undefined;
  }

  interface RenderField {
    name: string;
    label: string;
    widget: 'text' | 'number' | 'toggle' | 'select';
    options?: string[];
  }

  const fields = $derived.by((): RenderField[] => {
    const schema = getSchema(schemaName);
    if (!schema?.properties) return [];

    const list: RenderField[] = [];
    for (const [name, prop] of Object.entries(schema.properties)) {
      // Opt-in: a field only renders here if it explicitly declares a
      // ui_widget. Fields with real structural/custom UX (list management,
      // conditional nesting, calculated values) are meant to stay
      // hand-written in their own component and simply omit ui_widget.
      if (!prop.ui_widget || prop.ui_widget === 'hidden') continue;
      if (group !== undefined && prop.ui_group !== group) continue;

      list.push({
        name,
        label: prop.ui_label ?? name,
        widget: prop.ui_widget,
        options: prop.ui_options
      });
    }

    return list.sort((a, b) => {
      const oa = (getSchema(schemaName)?.properties?.[a.name]?.ui_order as number) ?? 0;
      const ob = (getSchema(schemaName)?.properties?.[b.name]?.ui_order as number) ?? 0;
      return oa - ob;
    });
  });

  function fieldId(name: string) {
    return `${schemaName}-${name}`;
  }
</script>

<div class="flex flex-wrap items-end gap-3">
  {#each fields as field (field.name)}
    {#if field.widget === 'toggle'}
      <Toggle
        bind:checked={data[field.name]}
        label={field.label}
        disabled={disabledFields.includes(field.name)}
      />
    {:else if field.widget === 'select' && field.options}
      <div class="space-y-1">
        <Label for={fieldId(field.name)}>{field.label}</Label>
        <Select
          id={fieldId(field.name)}
          value={data[field.name] as string}
          disabled={disabledFields.includes(field.name)}
          onchange={(e: Event) => {
            data[field.name] = (e.target as HTMLSelectElement).value;
            onchange?.();
          }}
        >
          {#each field.options as opt (opt)}
            <option value={opt}>{opt}</option>
          {/each}
        </Select>
      </div>
    {:else}
      <div class="space-y-1">
        <Label for={fieldId(field.name)}>{field.label}</Label>
        <Input
          id={fieldId(field.name)}
          type={field.widget === 'number' ? 'number' : 'text'}
          value={data[field.name] as string | number}
          disabled={disabledFields.includes(field.name)}
          oninput={(e: Event) => {
            const raw = (e.target as HTMLInputElement).value;
            data[field.name] = field.widget === 'number' && raw !== '' ? Number(raw) : raw;
            onchange?.();
          }}
          clearable={field.widget === 'number'}
        />
      </div>
    {/if}
  {/each}
</div>
