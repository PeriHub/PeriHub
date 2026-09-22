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

  // ---------------------------------------------------------------------
  // Generic dimensional conversion system
  //
  // Every mechanical quantity below is expressed as a combination of three
  // independent base-unit exponents relative to SI (N, m, kg):
  //   forceExp  -> exponent of Newton   (N)
  //   lengthExp -> exponent of metre    (m)
  //   massExp   -> exponent of kilogram (kg)
  //
  // The three target systems are:
  //   mm -> "SI (mm)": N, mm, tonne (consistent N-mm-tonne-s system used in FEA)
  //   ft -> "US (ft)": lbf, ft, slug
  //   in -> "US (in)": lbf, in, lbf·s²/in
  //
  // A quantity's conversion factor for a given column is simply
  //   FORCE[col]^forceExp * LENGTH[col]^lengthExp * MASS[col]^massExp
  // ---------------------------------------------------------------------

  type ColKey = 'si' | 'mm' | 'ft' | 'in';

  const FORCE: Record<ColKey, number> = { si: 1, mm: 1, ft: 0.22480894, in: 0.22480894 };
  const LENGTH: Record<ColKey, number> = { si: 1, mm: 1000, ft: 3.2808399, in: 39.37007874 };
  const MASS: Record<ColKey, number> = { si: 1, mm: 0.001, ft: 0.06852177, in: 0.00571015 };

  function factor(forceExp: number, lengthExp: number, massExp: number, col: ColKey): number {
    return FORCE[col] ** forceExp * LENGTH[col] ** lengthExp * MASS[col] ** massExp;
  }

  type QuantityKey =
    | 'length'
    | 'force'
    | 'mass'
    | 'velocity'
    | 'acceleration'
    | 'moment'
    | 'pressure'
    | 'density'
    | 'energy'
    | 'energyReleaseRate'
    | 'fractureToughness';

  interface QuantityDef {
    key: QuantityKey;
    label: string;
    units: Record<ColKey, string>;
    forceExp: number;
    lengthExp: number;
    massExp: number;
  }

  const quantities: QuantityDef[] = [
    {
      key: 'length',
      label: 'Length',
      units: { si: 'm', mm: 'mm', ft: 'ft', in: 'in' },
      forceExp: 0,
      lengthExp: 1,
      massExp: 0
    },
    {
      key: 'force',
      label: 'Force',
      units: { si: 'N', mm: 'N', ft: 'lbf', in: 'lbf' },
      forceExp: 1,
      lengthExp: 0,
      massExp: 0
    },
    {
      key: 'mass',
      label: 'Mass',
      units: { si: 'kg', mm: 't', ft: 'slug', in: 'lbf·s²/in' },
      forceExp: 0,
      lengthExp: 0,
      massExp: 1
    },
    {
      key: 'velocity',
      label: 'Velocity',
      units: { si: 'm/s', mm: 'mm/s', ft: 'ft/s', in: 'in/s' },
      forceExp: 0,
      lengthExp: 1,
      massExp: 0
    },
    {
      key: 'acceleration',
      label: 'Acceleration',
      units: { si: 'm/s²', mm: 'mm/s²', ft: 'ft/s²', in: 'in/s²' },
      forceExp: 0,
      lengthExp: 1,
      massExp: 0
    },
    {
      key: 'moment',
      label: 'Moment',
      units: { si: 'N·m', mm: 'N·mm', ft: 'lbf·ft', in: 'lbf·in' },
      forceExp: 1,
      lengthExp: 1,
      massExp: 0
    },
    {
      key: 'pressure',
      label: 'Pressure / Stress',
      units: { si: 'Pa', mm: 'MPa', ft: 'lbf/ft²', in: 'psi' },
      forceExp: 1,
      lengthExp: -2,
      massExp: 0
    },
    {
      key: 'density',
      label: 'Density',
      units: { si: 'kg/m³', mm: 't/mm³', ft: 'slug/ft³', in: 'lbf·s²/in⁴' },
      forceExp: 0,
      lengthExp: -3,
      massExp: 1
    },
    {
      key: 'energy',
      label: 'Energy',
      units: { si: 'J', mm: 'mJ', ft: 'ft·lbf', in: 'in·lbf' },
      forceExp: 1,
      lengthExp: 1,
      massExp: 0
    },
    {
      key: 'energyReleaseRate',
      label: 'Energy Release Rate',
      units: { si: 'N/m', mm: 'N/mm', ft: 'lbf/ft', in: 'lbf/in' },
      forceExp: 1,
      lengthExp: -1,
      massExp: 0
    },
    {
      key: 'fractureToughness',
      label: 'Fracture Toughness',
      units: { si: 'Pa·√m', mm: 'MPa·√mm', ft: 'lbf/ft²·√ft', in: 'psi·√in' },
      forceExp: 1,
      lengthExp: -1.5,
      massExp: 0
    }
  ];

  const cols: { key: ColKey; heading: string }[] = [
    { key: 'si', heading: 'SI' },
    { key: 'mm', heading: 'SI (mm)' },
    { key: 'ft', heading: 'US Unit (ft)' },
    { key: 'in', heading: 'US Unit (in)' }
  ];

  // Canonical value (in SI base units) per quantity, plus the text currently
  // shown in each of the four columns.
  let si = $state<Record<QuantityKey, number | null>>(
    Object.fromEntries(quantities.map((q) => [q.key, null])) as Record<QuantityKey, number | null>
  );
  let display = $state<Record<QuantityKey, Record<ColKey, string>>>(
    Object.fromEntries(
      quantities.map((q) => [q.key, { si: '', mm: '', ft: '', in: '' }])
    ) as Record<QuantityKey, Record<ColKey, string>>
  );

  function fmt(value: number): string {
    if (!Number.isFinite(value)) return '';
    const abs = Math.abs(value);
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e8)) return value.toExponential(6);
    return parseFloat(value.toPrecision(10)).toString();
  }

  function syncRow(qKey: QuantityKey, activeCol: ColKey) {
    const def = quantities.find((q) => q.key === qKey)!;
    const value = si[qKey];
    for (const c of cols) {
      if (c.key === activeCol) continue;
      display[qKey][c.key] =
        value == null ? '' : fmt(value * factor(def.forceExp, def.lengthExp, def.massExp, c.key));
    }
  }

  function handleInput(qKey: QuantityKey, col: ColKey, raw: string) {
    display[qKey][col] = raw;
    const def = quantities.find((q) => q.key === qKey)!;

    if (raw.trim() === '') {
      si[qKey] = null;
      for (const c of cols) if (c.key !== col) display[qKey][c.key] = '';
      persist();
      return;
    }

    const num = Number(raw);
    if (Number.isNaN(num)) return;

    si[qKey] = num / factor(def.forceExp, def.lengthExp, def.massExp, col);
    syncRow(qKey, col);
    persist();
  }

  function persist() {
    if (typeof window !== 'undefined') {
      localStorage.setItem('conversion-si', JSON.stringify(si));
    }
  }

  $effect(() => {
    if (typeof window === 'undefined') return;
    const saved = localStorage.getItem('conversion-si');
    if (!saved) return;
    try {
      const parsed = JSON.parse(saved) as Record<QuantityKey, number | null>;
      for (const q of quantities) {
        const value = parsed[q.key];
        if (value != null) {
          si[q.key] = value;
          for (const c of cols) {
            display[q.key][c.key] = fmt(value * factor(q.forceExp, q.lengthExp, q.massExp, c.key));
          }
        }
      }
    } catch {
      // ignore malformed storage
    }
  });

  async function copyText(qKey: QuantityKey, col: ColKey) {
    const value = display[qKey][col];
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      notify.info('Copied to clipboard');
    } catch {
      console.log('Error copying to clipboard');
    }
  }

  // ---------------------------------------------------------------------
  // Thermal quantities are kept as simple SI -> SI(mm) conversions, as
  // before. Temperature (K) is not converted between unit systems, so a
  // rigorous US-customary column is intentionally left out here.
  // ---------------------------------------------------------------------
  type ThermalKey = 'heatCapacity' | 'thermalConductivity';
  const thermalFields: { key: ThermalKey; inLabel: string; outLabel: string }[] = [
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
  let thermalIn = $state<Record<ThermalKey, number | null>>({
    heatCapacity: null,
    thermalConductivity: null
  });
  let thermalOut = $state<Record<ThermalKey, number | string | null>>({
    heatCapacity: null,
    thermalConductivity: null
  });

  function convertThermal() {
    if (thermalIn.heatCapacity != null) thermalOut.heatCapacity = thermalIn.heatCapacity * 1e9;
    if (thermalIn.thermalConductivity != null)
      thermalOut.thermalConductivity = thermalIn.thermalConductivity;
  }

  $effect(() => {
    const num = Object.values(thermalIn).filter((v) => v != null).length;
    if (num > 0) convertThermal();
    if (typeof window !== 'undefined') {
      localStorage.setItem('conversion-thermal', JSON.stringify(thermalIn));
    }
  });

  async function copyThermal(key: ThermalKey) {
    const value = thermalOut[key];
    if (value == null) return;
    try {
      await navigator.clipboard.writeText(String(value));
      notify.info('Copied to clipboard');
    } catch {
      console.log('Error copying to clipboard');
    }
  }
</script>

<Card class="w-full max-w-5xl p-5">
  <h2 class="text-lg font-semibold">Typical Conversions</h2>
  <p class="text-muted-foreground text-sm">
    Enter a value in any column — the other three update automatically.
  </p>

  <div class="border-border my-4 border-t"></div>

  <div class="overflow-x-auto">
    <div class="min-w-[860px]">
      <div
        class="text-muted-foreground grid grid-cols-[11rem_repeat(4,1fr)] gap-3 pb-2 text-sm font-medium"
      >
        <div>Quantity</div>
        {#each cols as c (c.key)}
          <div>{c.heading}</div>
        {/each}
      </div>

      <div class="max-h-[32rem] space-y-3 overflow-y-auto pr-1">
        {#each quantities as q (q.key)}
          <div class="grid grid-cols-[11rem_repeat(4,1fr)] items-center gap-3">
            <div class="text-sm font-medium">{q.label}</div>
            {#each cols as c (c.key)}
              <div class="space-y-1">
                <Label for={`${q.key}-${c.key}`} class="text-muted-foreground text-xs">
                  {q.units[c.key]}
                </Label>
                <div class="relative">
                  <Input
                    id={`${q.key}-${c.key}`}
                    type="number"
                    class="pr-9"
                    value={display[q.key][c.key]}
                    oninput={(e: Event) =>
                      handleInput(q.key, c.key, (e.currentTarget as HTMLInputElement).value)}
                  />
                  <button
                    type="button"
                    class="text-muted-foreground hover:text-foreground absolute inset-y-0 right-2 flex items-center"
                    onclick={() => copyText(q.key, c.key)}
                    title="Copy"
                  >
                    <Copy class="h-4 w-4" />
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/each}
      </div>
    </div>
  </div>
</Card>

<Card class="mt-4 w-full max-w-2xl p-5">
  <h2 class="text-lg font-semibold">Thermal Conversions (SI only)</h2>
  <p class="text-muted-foreground text-sm">
    Temperature (K) is not converted, so only SI and SI (mm) are shown here.
  </p>

  <div class="border-border my-4 border-t"></div>

  <div class="space-y-3">
    {#each thermalFields as f (f.key)}
      <div class="grid grid-cols-2 items-end gap-4">
        <div class="space-y-1">
          <Label for={`th-in-${f.key}`}>{f.inLabel}</Label>
          <Input id={`th-in-${f.key}`} type="number" bind:value={thermalIn[f.key]} />
        </div>
        <div class="space-y-1">
          <Label for={`th-out-${f.key}`}>{f.outLabel}</Label>
          <div class="relative">
            <Input id={`th-out-${f.key}`} readonly value={thermalOut[f.key] ?? ''} class="pr-9" />
            <button
              type="button"
              class="text-muted-foreground hover:text-foreground absolute inset-y-0 right-2 flex items-center"
              onclick={() => copyThermal(f.key)}
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
