<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!-- Fields of one material - used by the Material expansion and the /materials library page. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import {
    convertElasticConstants,
    emptyElasticConstants,
    orthotropicStiffness
  } from '$lib/utils/elastic-constants';
  import { Trash2 } from 'lucide-svelte';
  import type { Material, properties as MaterialProperties } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import ChipGroup from '$lib/components/ui/ChipGroup.svelte';

  let {
    material = $bindable(),
    idPrefix,
    userTools
  }: {
    material: Material;
    /** Unique per editor on the page - prefixes the field ids. */
    idPrefix: string;
    /** Extra controls for 'User' materials (file uploads, state variables) - model context only. */
    userTools?: Snippet;
  } = $props();

  const materialModelNames = [
    'Bond-based Elastic',
    'PD Solid Elastic',
    'PD Solid Plastic',
    'Correspondence Elastic',
    'Correspondence Plastic'
  ];
  const materialSymmetries = ['Isotropic', 'Anisotropic', 'Orthotropic', 'Transverse Isotropic'];
  const stabilizationTypes = ['Bond Based', 'State Based', 'Sub Horizon', 'Global Stiffness'];

  // Any two isotropic constants determine the other two - shown as
  // placeholders so an empty field reads as "calculated", not "missing".
  function derivedElastic(m: Material) {
    const set = (v: number | null | undefined) => (v == null || (v as unknown) === '' ? null : v);
    return convertElasticConstants({
      ...emptyElasticConstants(),
      poissonsRatio: set(m.poissonsRatio),
      bulkModulus: set(m.bulkModulus),
      shearModulus: set(m.shearModulus),
      youngsModulus: set(m.youngsModulus)
    });
  }

  function hint(v: number | null) {
    return v != null && Number.isFinite(v) ? `≈ ${+v.toPrecision(4)}` : undefined;
  }

  function calculateStiffnessMatrix() {
    const sm = material.stiffnessMatrix;
    if (!sm?.calculateStiffnessMatrix) return;

    const E1 = sm.engineeringConstants.E1 as number | null;
    const E2 = sm.engineeringConstants.E2 as number | null;
    let E3 = sm.engineeringConstants.E3 as number | null;
    const G12 = sm.engineeringConstants.G12 as number | null;
    let G13 = sm.engineeringConstants.G13 as number | null;
    let G23 = sm.engineeringConstants.G23 as number | null;
    const nu12 = sm.engineeringConstants.nu12 as number | null;
    let nu13 = sm.engineeringConstants.nu13 as number | null;
    let nu23 = sm.engineeringConstants.nu23 as number | null;

    if (E1 == null || E2 == null || G12 == null || nu12 == null) return;

    if (E3 == null) E3 = E2;
    if (G13 == null) G13 = G12;
    if (nu13 == null) nu13 = nu12;
    if (nu23 == null) nu23 = nu12;
    if (G23 == null) G23 = E2 / (2 * (1 + nu23));

    sm.matrix = orthotropicStiffness(E1, E2, E3, G12, G13, G23, nu12, nu13, nu23);
  }

  function addProp() {
    if (!material.properties) material.properties = [];
    const len = material.properties.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(material.properties[len - 1])) as MaterialProperties)
        : ({} as MaterialProperties);
    newItem.materialsPropId = len + 1;
    newItem.name = `Prop_${len + 1}`;
    material.properties.push(newItem);
  }

  function removeProp(subindex: number) {
    material.properties!.splice(subindex, 1);
  }
</script>

<div class="max-w-xs space-y-1">
  <Label for={`${idPrefix}-name`}>Name</Label>
  <Input id={`${idPrefix}-name`} bind:value={material.name} />
</div>

<div class="space-y-1">
  <Label>Material models</Label>
  <ChipGroup
    ariaLabel="Material models of {material.name}"
    options={materialModelNames}
    bind:value={material.matType}
  />
</div>

{#if material.matType?.includes('User')}
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
          onclick={() => removeProp(subindex)}
          title="Remove Property"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    {/each}
    <div class="flex flex-wrap items-end gap-2">
      <AddButton noun="property" items={material.properties} onclick={() => addProp()} />
      {@render userTools?.()}
    </div>
  </div>
{/if}

{#if material.materialSymmetry === 'Isotropic'}
  {@const calc = derivedElastic(material)}
  <div class="flex flex-wrap items-end gap-3">
    <div class="space-y-1">
      <Label for={`${idPrefix}-pr`}>Poisson's ratio</Label>
      <Input
        id={`${idPrefix}-pr`}
        type="number"
        placeholder={hint(calc.poissonsRatio)}
        bind:value={material.poissonsRatio}
      />
    </div>
    <div class="space-y-1">
      <Label for={`${idPrefix}-bulk`}>Bulk modulus</Label>
      <Input
        id={`${idPrefix}-bulk`}
        type="number"
        placeholder={hint(calc.bulkModulus)}
        bind:value={material.bulkModulus}
      />
    </div>
    <div class="space-y-1">
      <Label for={`${idPrefix}-shear`}>Shear modulus</Label>
      <Input
        id={`${idPrefix}-shear`}
        type="number"
        placeholder={hint(calc.shearModulus)}
        bind:value={material.shearModulus}
      />
    </div>
    <div class="space-y-1">
      <Label for={`${idPrefix}-young`}>Young's modulus</Label>
      <Input
        id={`${idPrefix}-young`}
        type="number"
        placeholder={hint(calc.youngsModulus)}
        bind:value={material.youngsModulus}
      />
    </div>
  </div>
{/if}

<div class="flex flex-wrap items-end gap-3">
  <div class="space-y-1">
    <Label for={`${idPrefix}-sym`}>Material symmetry</Label>
    <Select id={`${idPrefix}-sym`} bind:value={material.materialSymmetry}>
      {#each materialSymmetries as sym (sym)}
        <option value={sym}>{sym}</option>
      {/each}
    </Select>
  </div>
  <Toggle bind:checked={material.planeStress} label="Plane stress" />
  <Toggle bind:checked={material.planeStrain} label="Plane strain" />
  {#if material.stiffnessMatrix && material.materialSymmetry === 'Anisotropic' && material.matType?.includes('Correspondence')}
    <Toggle
      bind:checked={material.stiffnessMatrix.calculateStiffnessMatrix}
      label="Calculate stiffness matrix"
    />
  {/if}
</div>

{#if material.materialSymmetry === 'Transverse Isotropic' || material.materialSymmetry === 'Orthotropic'}
  <div class="flex flex-wrap items-end gap-3">
    <div class="space-y-1">
      <Label for={`${idPrefix}-ex`}>Young's modulus X</Label>
      <Input id={`${idPrefix}-ex`} type="number" bind:value={material.youngsModulusX} />
    </div>
    <div class="space-y-1">
      <Label for={`${idPrefix}-ey`}>Young's modulus Y</Label>
      <Input id={`${idPrefix}-ey`} type="number" bind:value={material.youngsModulusY} />
    </div>
    {#if material.materialSymmetry === 'Orthotropic'}
      <div class="space-y-1">
        <Label for={`${idPrefix}-ez`}>Young's modulus Z</Label>
        <Input id={`${idPrefix}-ez`} type="number" bind:value={material.youngsModulusZ} />
      </div>
    {/if}
    <div class="space-y-1">
      <Label for={`${idPrefix}-pxy`}>Poisson's ratio XY</Label>
      <Input id={`${idPrefix}-pxy`} type="number" bind:value={material.poissonsRatioXY} />
    </div>
    {#if material.planeStrain || material.materialSymmetry === 'Orthotropic'}
      <div class="space-y-1">
        <Label for={`${idPrefix}-pyz`}>Poisson's ratio YZ</Label>
        <Input id={`${idPrefix}-pyz`} type="number" bind:value={material.poissonsRatioYZ} />
      </div>
    {/if}
    {#if material.materialSymmetry === 'Orthotropic'}
      <div class="space-y-1">
        <Label for={`${idPrefix}-pxz`}>Poisson's ratio XZ</Label>
        <Input id={`${idPrefix}-pxz`} type="number" bind:value={material.poissonsRatioXZ} />
      </div>
    {/if}
    <div class="space-y-1">
      <Label for={`${idPrefix}-gxy`}>Shear modulus XY</Label>
      <Input id={`${idPrefix}-gxy`} type="number" bind:value={material.shearModulusXY} />
    </div>
    {#if material.materialSymmetry === 'Orthotropic'}
      <div class="space-y-1">
        <Label for={`${idPrefix}-gyz`}>Shear modulus YZ</Label>
        <Input id={`${idPrefix}-gyz`} type="number" bind:value={material.shearModulusYZ} />
      </div>
      <div class="space-y-1">
        <Label for={`${idPrefix}-gxz`}>Shear modulus XZ</Label>
        <Input id={`${idPrefix}-gxz`} type="number" bind:value={material.shearModulusXZ} />
      </div>
    {/if}
  </div>
{/if}

{#if material.stiffnessMatrix && material.materialSymmetry === 'Anisotropic' && material.matType?.includes('Correspondence')}
  <div class="border-border flex flex-wrap gap-6 border-t pt-3">
    {#if material.stiffnessMatrix.calculateStiffnessMatrix}
      <div class="space-y-2">
        {#each Object.keys(material.stiffnessMatrix.engineeringConstants) as key (key)}
          <div class="space-y-1">
            <Label for={`${idPrefix}-ec-${key}`}>{key}</Label>
            <Input
              id={`${idPrefix}-ec-${key}`}
              type="number"
              bind:value={
                material.stiffnessMatrix.engineeringConstants[
                  key as keyof typeof material.stiffnessMatrix.engineeringConstants
                ]
              }
              oninput={() => calculateStiffnessMatrix()}
            />
          </div>
        {/each}
      </div>
    {/if}
    <div class="space-y-2">
      {#each Object.keys(material.stiffnessMatrix.matrix) as key (key)}
        <div class="space-y-1">
          <Label for={`${idPrefix}-mx-${key}`}>{key}</Label>
          <Input
            id={`${idPrefix}-mx-${key}`}
            type="number"
            bind:value={
              material.stiffnessMatrix.matrix[key as keyof typeof material.stiffnessMatrix.matrix]
            }
            readonly={material.stiffnessMatrix.calculateStiffnessMatrix}
          />
        </div>
      {/each}
    </div>
  </div>
{/if}

<div class="max-w-xs space-y-1">
  <Label for={`${idPrefix}-stab`}>Stabilization type</Label>
  <Select id={`${idPrefix}-stab`} bind:value={material.stabilizationType}>
    {#each stabilizationTypes as type (type)}
      <option value={type}>{type}</option>
    {/each}
  </Select>
</div>

{#if material.matType?.some((t) => t.includes('Plastic'))}
  <div class="space-y-1">
    <Label for={`${idPrefix}-yield`}>Yield stress</Label>
    <Input id={`${idPrefix}-yield`} type="number" bind:value={material.yieldStress} />
  </div>
{/if}
