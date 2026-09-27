<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import CopyValue from './CopyValue.svelte';
  import {
    convertElasticConstants,
    emptyElasticConstants,
    type ElasticConstants
  } from '$lib/utils/elastic-constants';

  const materialKeys: Record<keyof ElasticConstants, string> = {
    bulkModulus: 'Bulk modulus K',
    shearModulus: 'Shear modulus G',
    youngsModulus: "Young's modulus E",
    poissonsRatio: "Poisson's ratio ν",
    pWaveModulus: 'P-wave modulus M',
    lameFirst: "Lamé's first parameter λ"
  };

  type Key = keyof ElasticConstants;

  let constants = $state<ElasticConstants>(emptyElasticConstants());

  const known = $derived(Object.values(constants).filter((v) => v != null).length);
  const calculated = $derived(convertElasticConstants(constants));

  const status = $derived(
    known === 2
      ? 'All six constants computed.'
      : known < 2
        ? `Enter ${2 - known} more constant${known === 1 ? '' : 's'}.`
        : `${known} constants entered — clear ${known - 2} to compute.`
  );

  // toPrecision(10) strips float noise such as 1.7499999999999997e+11.
  const fmt = (v: number) => Number(v.toPrecision(10)).toExponential();
</script>

<div class="divide-border divide-y">
  {#each Object.entries(materialKeys) as [key, label] (key)}
    {@const result = calculated[key as Key]}
    <div
      class="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] items-center gap-x-4 gap-y-1 py-2 sm:grid-cols-[12rem_12rem_minmax(0,1fr)]"
    >
      <label for={`in-${key}`} class="col-span-2 text-sm font-medium sm:col-span-1">{label}</label>
      <Input id={`in-${key}`} type="number" clearable bind:value={constants[key as Key]} />
      <div class="min-w-0">
        {#if result != null}<CopyValue value={fmt(result)} {label} />{/if}
      </div>
    </div>
  {/each}
</div>
<div class="mt-3 flex items-center justify-between gap-4">
  <p class="text-muted-foreground text-sm" aria-live="polite">{status}</p>
  <Button
    variant="ghost"
    disabled={known === 0}
    onclick={() => (constants = emptyElasticConstants())}
  >
    Clear all
  </Button>
</div>
