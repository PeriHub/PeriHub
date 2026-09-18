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

  const inputKeys = ['E1', 'E2', 'E3', 'G12', 'G13', 'G23', 'nu12', 'nu13', 'nu23'] as const;
  type InputKey = (typeof inputKeys)[number];

  type CKey =
    | 'C11'
    | 'C12'
    | 'C13'
    | 'C14'
    | 'C15'
    | 'C16'
    | 'C22'
    | 'C23'
    | 'C24'
    | 'C25'
    | 'C26'
    | 'C33'
    | 'C34'
    | 'C35'
    | 'C36'
    | 'C44'
    | 'C45'
    | 'C46'
    | 'C55'
    | 'C56'
    | 'C66';

  let constants = $state<Record<InputKey, number | null>>({
    E1: null,
    E2: null,
    E3: null,
    G12: null,
    G13: null,
    G23: null,
    nu12: null,
    nu13: null,
    nu23: null
  });

  let calculated = $state<Record<CKey, number | null>>(
    Object.fromEntries(
      [
        'C11', 'C12', 'C13', 'C14', 'C15', 'C16',
        'C22', 'C23', 'C24', 'C25', 'C26',
        'C33', 'C34', 'C35', 'C36',
        'C44', 'C45', 'C46',
        'C55', 'C56',
        'C66'
      ].map((k) => [k, null])
    ) as Record<CKey, number | null>
  );
  let stiffnessString = $state('');

  let initialized = $state(false);

  function resetResult() {
    for (const key of Object.keys(calculated) as CKey[]) calculated[key] = null;
    stiffnessString = '';
  }

  function convert() {
    const { E1, E2, E3, G12, G13, G23, nu12, nu13, nu23 } = constants as Record<InputKey, number>;

    calculated.C11 = 1 / E1;
    calculated.C22 = 1 / E2;
    calculated.C33 = 1 / E3;
    calculated.C12 = nu12 / E1;
    calculated.C13 = nu13 / E1;
    calculated.C23 = nu23 / E2;
    calculated.C44 = 1 / G12;
    calculated.C55 = 1 / G13;
    calculated.C66 = 1 / G23;
    calculated.C46 = (1 - nu12) / E1;
    calculated.C36 = (1 - nu13) / E1;
    calculated.C26 = (1 - nu23) / E2;
    calculated.C14 = calculated.C15 = calculated.C24 = nu12 / E2;
    calculated.C25 = calculated.C34 = calculated.C16 = nu13 / E3;
    calculated.C35 = calculated.C26 = calculated.C45 = nu23 / E3;
    calculated.C56 = (1 - nu12 - nu23) / E3;

    const stiffnessMatrix = [
      [calculated.C11, calculated.C12, calculated.C13, calculated.C14, calculated.C15, calculated.C16],
      [calculated.C22, calculated.C23, calculated.C24, calculated.C25, calculated.C26],
      [calculated.C33, calculated.C34, calculated.C35, calculated.C36],
      [calculated.C44, calculated.C45, calculated.C46],
      [calculated.C55, calculated.C56],
      [calculated.C66]
    ];
    const names = [
      ['C11', 'C12', 'C13', 'C14', 'C15', 'C16'],
      ['C22', 'C23', 'C24', 'C25', 'C26'],
      ['C33', 'C34', 'C35', 'C36'],
      ['C44', 'C45', 'C46'],
      ['C55', 'C56'],
      ['C66']
    ];

    let out = '';
    for (let i = 0; i < names.length; i++) {
      for (let j = 0; j < names[i]!.length; j++) {
        out += `${names[i]![j]}: ${stiffnessMatrix[i]![j]!.toFixed(4)}\n`;
      }
    }
    stiffnessString = out;
  }

  $effect.pre(() => {
    if (initialized || typeof window === 'undefined') return;
    initialized = true;
    const stored = localStorage.getItem('constants');
    if (stored) {
      try {
        constants = { ...constants, ...JSON.parse(stored) };
      } catch {
        /* ignore malformed cache */
      }
    }
  });

  $effect(() => {
    const num = Object.values(constants).filter((v) => v != null).length;
    if (num === 9) {
      convert();
    } else {
      resetResult();
    }
    if (typeof window !== 'undefined') {
      localStorage.setItem('constants', JSON.stringify(constants));
    }
  });

  async function copyText(value: string | null) {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      notify.info('Copied to clipboard');
    } catch {
      notify.negative('Failed to copy');
    }
  }
</script>

<Card class="w-full max-w-2xl p-5">
  <h2 class="text-lg font-semibold">Conversion of elastic isotropic constants</h2>
  <p class="text-sm text-muted-foreground">Enter all nine constants to run the calculation</p>

  <div class="my-4 border-t border-border"></div>

  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
    <div class="space-y-3">
      {#each inputKeys as key (key)}
        <div class="space-y-1">
          <Label for={`stiff-${key}`}>{key}</Label>
          <Input id={`stiff-${key}`} type="number" bind:value={constants[key]} />
        </div>
      {/each}
    </div>

    <div class="space-y-3">
      {#each ['C11', 'C12', 'C13', 'C14', 'C15', 'C16'] as key (key)}
        <div class="space-y-1">
          <Label for={`stiff-out-${key}`}>{key}</Label>
          <div class="relative">
            <Input id={`stiff-out-${key}`} readonly value={calculated[key as CKey] ?? ''} class="pr-9" />
            <button
              type="button"
              class="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground"
              onclick={() => copyText(String(calculated[key as CKey] ?? ''))}
              title="Copy"
            >
              <Copy class="h-4 w-4" />
            </button>
          </div>
        </div>
      {/each}
      <div class="space-y-1">
        <Label for="stiff-out-string">Full matrix</Label>
        <div class="relative">
          <textarea
            id="stiff-out-string"
            readonly
            rows="6"
            value={stiffnessString}
            class="w-full rounded-md border border-input bg-background p-2 pr-9 font-mono text-xs"
          ></textarea>
          <button
            type="button"
            class="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
            onclick={() => copyText(stiffnessString)}
            title="Copy"
          >
            <Copy class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</Card>
