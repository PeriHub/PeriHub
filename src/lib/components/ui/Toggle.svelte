<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Switch } from 'bits-ui';
  import Label from '$lib/components/ui/Label.svelte';

  interface Props {
    checked?: boolean | null;
    label?: string;
    disabled?: boolean;
    id?: string;
    onCheckedChange?: (checked: boolean) => void;
  }

  let { checked = $bindable(), label, disabled = false, id, onCheckedChange }: Props = $props();
  const inputId = id ?? label?.replace(/\s+/g, '-').toLowerCase();

  // bits-ui's own Switch.Root has the same fallback-vs-bind restriction
  // internally, so passing an upstream `undefined` straight through via
  // `bind:checked` would just hit the identical crash one level deeper.
  // Instead, Switch.Root is driven as a controlled component (plain
  // `checked` prop + `onCheckedChange`) fed by this always-boolean local
  // state, kept in sync with whatever the caller's value currently is.
  let localChecked = $state(checked ?? false);

  $effect(() => {
    localChecked = checked ?? false;
  });

  function handleCheckedChange(value: boolean) {
    localChecked = value;
    checked = value;
  }
</script>

<div class="flex items-center gap-2">
  <Switch.Root
    checked={localChecked}
    onCheckedChange={onCheckedChange ?? handleCheckedChange}
    {disabled}
    id={inputId}
    class="peer bg-muted data-[state=checked]:bg-primary bg-muted data-[state=checked]:bg-primary inline-flex h-5 w-9 shrink-0 items-center rounded-full border border-transparent transition-colors disabled:cursor-not-allowed disabled:opacity-50"
  >
    <Switch.Thumb
      class="pointer-events-none block h-4 w-4 rounded-full bg-white shadow-sm transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0.5"
    />
  </Switch.Root>
  {#if label}
    <Label for={inputId} class="cursor-pointer font-normal">{label}</Label>
  {/if}
</div>
