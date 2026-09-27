<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import Input from '$lib/components/ui/Input.svelte';
  import CopyValue from './CopyValue.svelte';

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
    | 'fractureToughness'
    | 'heatCapacity'
    | 'thermalConductivity';

  interface QuantityDef {
    key: QuantityKey;
    label: string;
    units: Record<ColKey, string>;
    forceExp: number;
    lengthExp: number;
    massExp: number;
    // Temperature stays in kelvin, so thermal quantities only convert between SI and SI (mm).
    siOnly?: boolean;
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
    },
    {
      key: 'heatCapacity',
      label: 'Specific Heat Capacity',
      units: { si: 'J/kg·K', mm: 'mJ/t·K', ft: '', in: '' },
      forceExp: 1,
      lengthExp: 1,
      massExp: -1,
      siOnly: true
    },
    {
      key: 'thermalConductivity',
      label: 'Thermal Conductivity',
      units: { si: 'W/m·K', mm: 'mW/mm·K', ft: '', in: '' },
      forceExp: 1,
      lengthExp: 0,
      massExp: 0,
      siOnly: true
    }
  ];

  // The column a row is typed in: the chosen system, or SI for thermal rows when a US system is chosen.
  const inCol = (q: QuantityDef): ColKey =>
    q.siOnly && (from === 'ft' || from === 'in') ? 'si' : from;

  const cols: { key: ColKey; heading: string }[] = [
    { key: 'si', heading: 'SI' },
    { key: 'mm', heading: 'SI (mm)' },
    { key: 'ft', heading: 'US Unit (ft)' },
    { key: 'in', heading: 'US Unit (in)' }
  ];

  // Canonical value (in SI base units) per quantity; `text` is what the input shows in the
  // chosen system, kept separately so typing "1e" or "0." isn't reformatted mid-keystroke.
  let from = $state<ColKey>('si');
  let si = $state<Record<QuantityKey, number | null>>(
    Object.fromEntries(quantities.map((q) => [q.key, null])) as Record<QuantityKey, number | null>
  );
  let text = $state<Record<QuantityKey, string>>(
    Object.fromEntries(quantities.map((q) => [q.key, ''])) as Record<QuantityKey, string>
  );

  function fmt(value: number): string {
    if (!Number.isFinite(value)) return '';
    const abs = Math.abs(value);
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e8))
      return Number(value.toPrecision(6)).toExponential();
    return parseFloat(value.toPrecision(6)).toString();
  }

  const convert = (q: QuantityDef, col: ColKey) =>
    si[q.key] == null ? '' : fmt(si[q.key]! * factor(q.forceExp, q.lengthExp, q.massExp, col));

  function handleInput(q: QuantityDef, raw: string) {
    text[q.key] = raw;
    const num = Number(raw);
    if (raw.trim() === '') si[q.key] = null;
    else if (!Number.isNaN(num))
      si[q.key] = num / factor(q.forceExp, q.lengthExp, q.massExp, inCol(q));
    localStorage.setItem('conversion-si', JSON.stringify(si));
  }

  function setFrom(col: ColKey) {
    from = col;
    for (const q of quantities) text[q.key] = convert(q, inCol(q));
  }

  if (typeof window !== 'undefined') {
    try {
      const saved = JSON.parse(localStorage.getItem('conversion-si') ?? '{}');
      for (const q of quantities) if (saved[q.key] != null) si[q.key] = saved[q.key];
      setFrom('si');
    } catch {
      // ignore malformed storage
    }
  }
</script>

<div class="overflow-x-auto">
  <table class="w-full min-w-[48rem] table-fixed border-collapse text-sm">
    <caption class="text-muted-foreground pb-2 text-left text-xs">
      Click a system to type in it. Thermal rows keep temperature in kelvin, so they only convert
      between SI and SI (mm).
    </caption>
    <colgroup>
      <col class="w-40" />
      {#each cols as c (c.key)}
        <col class={c.key === from ? 'w-64' : ''} />
      {/each}
    </colgroup>
    <thead>
      <tr class="border-border border-b">
        <th scope="col" class=" py-2 pr-3 text-left font-medium">Quantity</th>
        {#each cols as c (c.key)}
          <th scope="col" class="px-2 py-1 text-left font-medium">
            <button
              type="button"
              aria-pressed={from === c.key}
              onclick={() => setFrom(c.key)}
              class="focus-visible:ring-ring -mx-2 rounded-md px-2 py-1 transition-colors focus-visible:ring-2 focus-visible:outline-none {from ===
              c.key
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
            >
              {c.heading}
            </button>
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each quantities as q (q.key)}
        <tr class="border-border border-b last:border-b-0">
          <th scope="row" class="py-1.5 pr-3 text-left font-medium">
            <label for={`unit-${q.key}`}>{q.label}</label>
          </th>
          {#each cols as c (c.key)}
            <td class="px-2 py-1.5 align-middle">
              {#if q.siOnly && (c.key === 'ft' || c.key === 'in')}
                <span class="text-muted-foreground/60" aria-label="not converted">—</span>
              {:else if c.key === inCol(q)}
                <div class="flex items-center gap-1.5">
                  <Input
                    id={`unit-${q.key}`}
                    type="number"
                    class="min-w-0"
                    value={text[q.key]}
                    oninput={(e: Event) =>
                      handleInput(q, (e.currentTarget as HTMLInputElement).value)}
                  />
                  <span class="text-muted-foreground w-[4.5rem] shrink-0 font-mono text-xs"
                    >{q.units[c.key]}</span
                  >
                </div>
              {:else if si[q.key] != null}
                <CopyValue
                  value={convert(q, c.key)}
                  unit={q.units[c.key]}
                  label={`${q.label} in ${q.units[c.key]}`}
                />
              {:else}
                <span class="text-muted-foreground/60 font-mono text-xs">{q.units[c.key]}</span>
              {/if}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
