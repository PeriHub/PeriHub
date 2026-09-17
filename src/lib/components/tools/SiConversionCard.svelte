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

  type Key =
    | 'mass'
    | 'length'
    | 'velocity'
    | 'force'
    | 'acceleration'
    | 'moment'
    | 'pressure'
    | 'density'
    | 'densityLb'
    | 'densityGramm'
    | 'energy'
    | 'energyReleaseRate'
    | 'fractureToughness'
    | 'heatCapacity'
    | 'thermalConductivity';

  const fields: { key: Key; inLabel: string; outLabel: string }[] = [
    { key: 'mass', inLabel: 'Mass [kg]', outLabel: 'Mass [t]' },
    { key: 'length', inLabel: 'Length [m]', outLabel: 'Length [mm]' },
    { key: 'velocity', inLabel: 'Velocity [m/s]', outLabel: 'Velocity [mm/s]' },
    { key: 'force', inLabel: 'Force [N]', outLabel: 'Force [N]' },
    { key: 'acceleration', inLabel: 'Acceleration [m/s²]', outLabel: 'Acceleration [mm/s²]' },
    { key: 'moment', inLabel: 'Moment [Nm]', outLabel: 'Moment [Nmm]' },
    { key: 'pressure', inLabel: 'Pressure [Pa]', outLabel: 'Pressure [MPa]' },
    { key: 'density', inLabel: 'Density [kg/m³]', outLabel: 'Density [t/mm³]' },
    { key: 'densityLb', inLabel: 'Density [lb/in³]', outLabel: 'Density [t/mm³]' },
    { key: 'densityGramm', inLabel: 'Density [g/cm³]', outLabel: 'Density [t/mm³]' },
    { key: 'energy', inLabel: 'Energy [J]', outLabel: 'Energy [mJ]' },
    {
      key: 'energyReleaseRate',
      inLabel: 'Energy release rate [N/m]',
      outLabel: 'Energy release rate [N/mm]'
    },
    {
      key: 'fractureToughness',
      inLabel: 'Fracture Toughness [Pa·m^(1/2)]',
      outLabel: 'Fracture Toughness [MPa·mm^(1/2)]'
    },
    {
      key: 'heatCapacity',
      inLabel: 'Specific Heat Capacity [J/kg·K]',
      outLabel: 'Specific Heat Capacity [kJ/t·K]'
    },
    {
      key: 'thermalConductivity',
      inLabel: 'Thermal Conductivity [W/m·K]',
      outLabel: 'Thermal Conductivity [kW/mm·K]'
    }
  ];

  const empty = () =>
    Object.fromEntries(fields.map((f) => [f.key, null])) as Record<Key, number | null>;

  let conversion = $state<Record<Key, number | null>>(empty());
  let results = $state<Record<Key, number | string | null>>(empty());

  function convertTypical() {
    const c = conversion;
    if (c.mass != null) results.mass = c.mass / 1000;
    if (c.length != null) results.length = c.length * 1000;
    if (c.velocity != null) results.velocity = c.velocity * 1000;
    if (c.force != null) results.force = c.force;
    if (c.acceleration != null) results.acceleration = c.acceleration * 1000;
    if (c.moment != null) results.moment = c.moment * 1000;
    if (c.pressure != null) results.pressure = c.pressure / 1_000_000;
    if (c.density != null) results.density = c.density / Math.pow(10, 12);
    if (c.densityLb != null) results.densityLb = (c.densityLb * 0.000027679905) / 1000;
    if (c.densityGramm != null) results.densityGramm = c.densityGramm / Math.pow(10, 9);
    if (c.energy != null) results.energy = c.energy * 1000;
    if (c.energyReleaseRate != null) results.energyReleaseRate = c.energyReleaseRate / 1000;
    if (c.fractureToughness != null)
      results.fractureToughness = Math.sqrt(c.fractureToughness ** 2 / 1e9);
    if (c.heatCapacity != null) results.heatCapacity = c.heatCapacity * 1e9;
    if (c.thermalConductivity != null) results.thermalConductivity = c.thermalConductivity;
  }

  $effect(() => {
    const num = Object.values(conversion).filter((v) => v != null).length;
    if (num > 0) convertTypical();
    if (typeof window !== 'undefined') {
      localStorage.setItem('conversion', JSON.stringify(conversion));
    }
  });

  async function copyText(key: Key) {
    const value = results[key];
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
  <h2 class="text-lg font-semibold">Typical Conversions</h2>
  <p class="text-sm text-muted-foreground">Enter a constant to run the calculation</p>

  <div class="my-4 border-t border-border"></div>

  <div class="max-h-[32rem] space-y-3 overflow-y-auto pr-1">
    {#each fields as f (f.key)}
      <div class="grid grid-cols-2 items-end gap-4">
        <div class="space-y-1">
          <Label for={`si-in-${f.key}`}>{f.inLabel}</Label>
          <Input id={`si-in-${f.key}`} type="number" bind:value={conversion[f.key]} />
        </div>
        <div class="space-y-1">
          <Label for={`si-out-${f.key}`}>{f.outLabel}</Label>
          <div class="relative">
            <Input id={`si-out-${f.key}`} readonly value={results[f.key] ?? ''} class="pr-9" />
            <button
              type="button"
              class="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground"
              onclick={() => copyText(f.key)}
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
