<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Copy } from 'lucide-svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import { notify } from '$lib/utils/notify';
  import {
    convertElasticConstants,
    emptyElasticConstants,
    type ElasticConstants
  } from '$lib/utils/elastic-constants';

  const materialKeys: Record<keyof ElasticConstants, string> = {
    bulkModulus: 'Bulk Modulus (K)',
    shearModulus: 'Shear Modulus (G)',
    youngsModulus: "Young's Modulus (E)",
    poissonsRatio: "Poisson's Ratio (v)",
    pWaveModulus: 'P-wave modulus (M)',
    lameFirst: "Lamé's first parameter (λ)"
  };

  type Key = keyof ElasticConstants;

  let constants = $state<ElasticConstants>(emptyElasticConstants());
  let calculated = $state<Record<Key, number | string | null>>(emptyElasticConstants());

  $effect(() => {
    const result = convertElasticConstants(constants);
    for (const key of Object.keys(result) as Key[]) {
      const value = result[key];
      // Match the original UI convention: show computed values in exponential notation.
      calculated[key] = value != null ? value.toExponential() : null;
    }
    if (typeof window !== 'undefined') {
      localStorage.setItem('constants', JSON.stringify(constants));
    }
  });

  async function copyText(key: Key) {
    const value = calculated[key];
    if (value == null) return;
    try {
      await navigator.clipboard.writeText(String(value));
      notify.info('Copied to clipboard');
    } catch {
      console.log('Error copying to clipboard');
    }
  }
</script>

<Card class="w-full max-w-2xl p-5">
  <h2 class="text-lg font-semibold">Conversion of elastic isotropic constants</h2>
  <p class="text-sm text-muted-foreground">Enter two constants to run the calculations</p>

  <div class="my-4 border-t border-border"></div>

  <div class="space-y-3">
    {#each Object.entries(materialKeys) as [key, label] (key)}
      <div class="grid grid-cols-2 items-end gap-4">
        <div class="space-y-1">
          <Label for={`in-${key}`}>{label}</Label>
          <Input id={`in-${key}`} type="number" bind:value={constants[key as Key]} />
        </div>
        <div class="space-y-1">
          <Label for={`out-${key}`}>{label} (result)</Label>
          <div class="relative">
            <Input id={`out-${key}`} readonly value={calculated[key as Key] ?? ''} class="pr-9" />
            <button
              type="button"
              class="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground"
              onclick={() => copyText(key as Key)}
              title="Copy"
            >
              <Copy class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    {/each}
  </div>
</Card>
