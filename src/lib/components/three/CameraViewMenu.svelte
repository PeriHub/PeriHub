<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { DropdownMenu } from 'bits-ui';
  import { Camera } from 'lucide-svelte';
  import { buttonVariants } from '$lib/components/ui/Button.svelte';

  interface Props {
    // Camera position relative to the model center, e.g. scene.fitToPoints.
    onSelect: (direction: [number, number, number]) => void;
  }

  let { onSelect }: Props = $props();

  // Z-up (CameraRig switches to Y-up for flat 2D models, where Top is the
  // plane view).
  const views: { label: string; direction: [number, number, number] }[] = [
    { label: 'Top (+Z)', direction: [0, 0, 1] },
    { label: 'Bottom (−Z)', direction: [0, 0, -1] },
    { label: 'Front (−Y)', direction: [0, -1, 0] },
    { label: 'Back (+Y)', direction: [0, 1, 0] },
    { label: 'Right (+X)', direction: [1, 0, 0] },
    { label: 'Left (−X)', direction: [-1, 0, 0] },
    { label: 'Isometric', direction: [1, -1, 1] }
  ];
</script>

<DropdownMenu.Root>
  <DropdownMenu.Trigger
    class={buttonVariants({ variant: 'ghost', size: 'icon' })}
    title="Camera view"
    aria-label="Camera view"
  >
    <Camera class="h-4 w-4" />
  </DropdownMenu.Trigger>
  <DropdownMenu.Portal>
    <DropdownMenu.Content
      class="border-border bg-popover text-popover-foreground z-50 min-w-[160px] rounded-md border p-1 shadow-md"
      align="start"
    >
      {#each views as view (view.label)}
        <DropdownMenu.Item
          class="data-[highlighted]:bg-muted flex items-center rounded-sm px-2 py-1.5 text-sm outline-none"
          onSelect={() => onSelect(view.direction)}
        >
          {view.label}
        </DropdownMenu.Item>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Portal>
</DropdownMenu.Root>
