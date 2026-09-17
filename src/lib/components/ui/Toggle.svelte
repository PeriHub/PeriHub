<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Switch } from 'bits-ui';
  import Label from '$lib/components/ui/Label.svelte';

  interface Props {
    checked?: boolean;
    label?: string;
    disabled?: boolean;
    id?: string;
  }

  // No fallback on this bindable: several call sites bind directly to
  // optional backend fields (e.g. solver.matEnabled) that are genuinely
  // `undefined` until a value is set. Svelte disallows binding `undefined`
  // into a bindable prop that *has* a fallback ("Cannot do
  // bind:checked={undefined} when checked has a fallback value") - so this
  // prop intentionally has none, and undefined is normalized below instead.
  let { checked = $bindable(), label, disabled = false, id }: Props = $props();
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
    onCheckedChange={handleCheckedChange}
    {disabled}
    id={inputId}
    class="peer inline-flex h-5 w-9 shrink-0 items-center rounded-full border border-transparent bg-muted transition-colors data-[state=checked]:bg-primary disabled:cursor-not-allowed disabled:opacity-50"
  >
    <Switch.Thumb
      class="pointer-events-none block h-4 w-4 rounded-full bg-white shadow-sm transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0.5"
    />
  </Switch.Root>
  {#if label}
    <Label for={inputId} class="cursor-pointer font-normal">{label}</Label>
  {/if}
</div>
