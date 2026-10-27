<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!-- Fields of one material - used by the Material expansion and the /materials library page. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Trash2 } from 'lucide-svelte';
  import {
    convertElasticConstants,
    emptyElasticConstants,
    orthotropicStiffness
  } from '$lib/utils/elastic-constants';
  import type { EngineeringConstants, Material, MaterialProperty } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ChipGroup from '$lib/components/ui/ChipGroup.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import {
    sections,
    modelNames,
    pick,
    splitModels,
    joinModels,
    CUSTOM_KEYS
  } from '$lib/perilab/schema';

  let {
    material = $bindable(),
    idPrefix,
    userTools
  }: {
    material: Material;
    /** Unique per editor on the page - prefixes the field ids. */
    idPrefix: string;
    /** Extra controls for user materials (file uploads) - model context only. */
    userTools?: Snippet;
  } = $props();

  const params = $derived(material.params!);
  const selected = $derived(splitModels(params['Material Model']));
  const materialModelNames = $derived(
    pick(
      modelNames(sections.material),
      ['PD Solid Elastic', 'PD Solid Plastic', 'Correspondence Elastic', 'Correspondence Plastic'],
      selected
    )
  );
  const userMaterial = $derived(selected.some((m) => /UMAT|User/.test(m)));
  const anisotropic = $derived(String(params['Symmetry'] ?? '').startsWith('anisotropic'));

  // Any two isotropic constants determine the others - shown as placeholders so an empty field reads as
  // "calculated", not "missing".
  const num = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? v : null);
  const calc = $derived(
    convertElasticConstants({
      ...emptyElasticConstants(),
      poissonsRatio: num(params["Poisson's Ratio"]),
      bulkModulus: num(params['Bulk Modulus']),
      shearModulus: num(params['Shear Modulus']),
      youngsModulus: num(params["Young's Modulus"])
    })
  );
  const approx = (v: number | null) =>
    v != null && Number.isFinite(v) ? `≈ ${+v.toPrecision(4)}` : undefined;
  const hints = $derived({
    "Poisson's Ratio": approx(calc.poissonsRatio),
    'Bulk Modulus': approx(calc.bulkModulus),
    'Shear Modulus': approx(calc.shearModulus),
    "Young's Modulus": approx(calc.youngsModulus)
  });

  const ENGINEERING = ['E1', 'E2', 'E3', 'G12', 'G13', 'G23', 'nu12', 'nu13', 'nu23'] as const;

  function calculateStiffnessMatrix() {
    const ec = material.engineeringConstants;
    if (!ec?.calculate) return;
    const { E1, E2, G12, nu12 } = ec;
    if (E1 == null || E2 == null || G12 == null || nu12 == null) return;
    const E3 = ec.E3 ?? E2;
    const G13 = ec.G13 ?? G12;
    const nu13 = ec.nu13 ?? nu12;
    const nu23 = ec.nu23 ?? nu12;
    const G23 = ec.G23 ?? E2 / (2 * (1 + nu23));
    Object.assign(params, orthotropicStiffness(E1, E2, E3, G12, G13, G23, nu12, nu13, nu23));
  }

  function setModels(models: (string | number)[] | null | undefined) {
    const joined = joinModels(models ?? []);
    if (joined) params['Material Model'] = joined;
    else delete params['Material Model'];
  }

  function addProp() {
    const list = material.properties ?? (material.properties = []);
    const len = list.length;
    list.push({
      materialsPropId: len + 1,
      name: `Prop_${len + 1}`,
      value: null
    } as MaterialProperty);
  }
</script>

<div class="max-w-xs space-y-1">
  <Label for={`${idPrefix}-name`}>Name</Label>
  <Input id={`${idPrefix}-name`} bind:value={material.name} />
</div>

<div class="space-y-1">
  <ParamLabel
    key="Material Model"
    for={`${idPrefix}-models`}
    required
    prop={sections.material?.properties?.['Material Model']}
  />
  <ChipGroup
    ariaLabel="Material Model of {material.name}"
    options={materialModelNames}
    bind:value={() => selected, setModels}
  />
</div>

{#if userMaterial}
  <div class="border-border space-y-2 border-t pt-2">
    {#each material.properties ?? [] as prop, subindex (subindex)}
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`${idPrefix}-prop-${subindex}`}>{prop.name}</Label>
          <Input id={`${idPrefix}-prop-${subindex}`} type="number" bind:value={prop.value} />
        </div>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => material.properties!.splice(subindex, 1)}
          title="Remove Property"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    {/each}
    <div class="flex flex-wrap items-end gap-2">
      <AddButton noun="property" items={material.properties} onclick={addProp} />
      {@render userTools?.()}
    </div>
  </div>
{/if}

<SchemaParams
  entry={sections.material}
  values={params}
  names={selected}
  custom={CUSTOM_KEYS.material}
  {idPrefix}
  {hints}
/>

{#if anisotropic}
  <div class="border-border space-y-2 border-t pt-3">
    <Toggle
      checked={material.engineeringConstants?.calculate ?? false}
      onCheckedChange={(on: boolean) => {
        material.engineeringConstants ??= { calculate: false } as EngineeringConstants;
        material.engineeringConstants.calculate = on;
        calculateStiffnessMatrix();
      }}
      label="Calculate C11…C66 from engineering constants"
    />
    {#if material.engineeringConstants?.calculate}
      <div class="flex flex-wrap items-end gap-3">
        {#each ENGINEERING as key (key)}
          <div class="w-24 space-y-1">
            <Label for={`${idPrefix}-ec-${key}`}>{key}</Label>
            <Input
              id={`${idPrefix}-ec-${key}`}
              type="number"
              bind:value={material.engineeringConstants[key]}
              oninput={calculateStiffnessMatrix}
            />
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}
