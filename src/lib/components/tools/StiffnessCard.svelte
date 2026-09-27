<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Copy } from 'lucide-svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { copyText } from '$lib/utils/clipboard';

  // Laid out as the 3x3 grid shown in the UI: moduli, shear moduli, Poisson's ratios.
  const inputRows = [
    ['E1', 'E2', 'E3'],
    ['G12', 'G13', 'G23'],
    ['nu12', 'nu13', 'nu23']
  ] as const;
  type InputKey = (typeof inputRows)[number][number];
  const inputLabel = (k: InputKey) => k.replace('nu', 'ν');

  const STORAGE_KEY = 'orthotropic-constants';

  const emptyConstants = (): Record<InputKey, number | null> => ({
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

  let constants = $state(emptyConstants());
  if (typeof window !== 'undefined') {
    try {
      constants = { ...constants, ...JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}') };
    } catch {
      /* ignore malformed cache */
    }
  }

  const known = $derived(Object.values(constants).filter((v) => v != null).length);

  // Upper triangle of the symmetric 6x6 matrix, keyed C11..C66.
  const calculated = $derived.by((): Record<string, number> | null => {
    if (known !== 9) return null;
    const { E1, E2, E3, G12, G13, G23, nu12, nu13, nu23 } = constants as Record<InputKey, number>;
    const c: Record<string, number> = {};
    c.C11 = 1 / E1;
    c.C22 = 1 / E2;
    c.C33 = 1 / E3;
    c.C12 = nu12 / E1;
    c.C13 = nu13 / E1;
    c.C23 = nu23 / E2;
    c.C44 = 1 / G12;
    c.C55 = 1 / G13;
    c.C66 = 1 / G23;
    c.C46 = (1 - nu12) / E1;
    c.C36 = (1 - nu13) / E1;
    c.C26 = (1 - nu23) / E2;
    c.C14 = c.C15 = c.C24 = nu12 / E2;
    c.C25 = c.C34 = c.C16 = nu13 / E3;
    c.C35 = c.C26 = c.C45 = nu23 / E3;
    c.C56 = (1 - nu12 - nu23) / E3;
    return c;
  });

  const idx = [1, 2, 3, 4, 5, 6];
  const fmt = (v: number) => v.toExponential(4);

  $effect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(constants));
  });

  function copyMatrix() {
    if (!calculated) return;
    const lines = idx.flatMap((i) =>
      idx.filter((j) => j >= i).map((j) => `C${i}${j}: ${fmt(calculated[`C${i}${j}`]!)}`)
    );
    copyText(lines.join('\n'));
  }
</script>

<div>
  <div class="grid grid-cols-3 gap-3">
    {#each inputRows as row (row[0])}
      {#each row as key (key)}
        <div class="space-y-1">
          <label for={`stiff-${key}`} class="font-mono text-xs font-medium">
            {inputLabel(key)}
          </label>
          <Input id={`stiff-${key}`} type="number" clearable bind:value={constants[key]} />
        </div>
      {/each}
    {/each}
  </div>

  <div class="mt-6 overflow-x-auto">
    <table class="w-full min-w-[40rem] table-fixed border-collapse font-mono text-xs">
      <caption class="sr-only">Upper triangle of the symmetric 6×6 matrix</caption>
      <tbody>
        {#each idx as i (i)}
          <tr>
            {#each idx as j (j)}
              <td class="border-border h-12 border p-0">
                {#if j < i}
                  <span class="text-muted-foreground/40 block text-center" aria-hidden="true"
                    >·</span
                  >
                {:else if calculated}
                  <button
                    type="button"
                    onclick={() => copyText(fmt(calculated[`C${i}${j}`]!))}
                    aria-label={`Copy C${i}${j}`}
                    class="hover:bg-muted focus-visible:ring-ring flex h-full w-full flex-col justify-center px-2 text-left focus-visible:ring-2 focus-visible:outline-none focus-visible:ring-inset"
                  >
                    <span class="text-muted-foreground text-[10px]">C{i}{j}</span>
                    <span class="truncate">{fmt(calculated[`C${i}${j}`]!)}</span>
                  </button>
                {:else}
                  <span class="text-muted-foreground block px-2 text-[10px]">C{i}{j}</span>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
    <p class="text-muted-foreground text-sm" aria-live="polite">
      {known === 9 ? 'Matrix computed.' : `${known} of 9 constants entered.`}
    </p>
    <div class="flex gap-2">
      <Button variant="ghost" disabled={known === 0} onclick={() => (constants = emptyConstants())}>
        Clear all
      </Button>
      <Button disabled={!calculated} onclick={copyMatrix}>
        <Copy class="h-4 w-4" /> Copy matrix
      </Button>
    </div>
  </div>
</div>
