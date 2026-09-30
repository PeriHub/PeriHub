<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Accordion } from 'bits-ui';
  import type { Component } from 'svelte';
  import {
    Box,
    Grid3x3,
    Wrench,
    Flame,
    Layers,
    Scissors,
    Grid2x2,
    Boxes,
    Waypoints,
    Filter,
    LogOut,
    Calculator,
    BarChart3
  } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { sectionStatus } from '$lib/utils/schemaValidation';
  import type { Contact, Deviations, Model, ModelData } from '$lib/client';
  import AccordionItem from '$lib/components/ui/AccordionItem.svelte';

  import ModelSettings from '$lib/components/expansions/Model.svelte';
  import DiscretizationSettings from '$lib/components/expansions/Discretization.svelte';
  import MaterialSettings from '$lib/components/expansions/Material.svelte';
  import ThermalSettings from '$lib/components/expansions/Thermal.svelte';
  import AdditiveSettings from '$lib/components/expansions/Additive.svelte';
  import DamageSettings from '$lib/components/expansions/Damage.svelte';
  import BlocksSettings from '$lib/components/expansions/Blocks.svelte';
  import ContactSettings from '$lib/components/expansions/Contact.svelte';
  import BoundaryConditionsSettings from '$lib/components/expansions/BoundaryConditions.svelte';
  import BondFilterSettings from '$lib/components/expansions/BondFilters.svelte';
  import OutputSettings from '$lib/components/expansions/Output.svelte';
  import SolverSettings from '$lib/components/expansions/Solver.svelte';
  import DeviationsSettings from '$lib/components/expansions/Deviations.svelte';

  // Data-driven panel config instead of 14 hand-copied AccordionItems with a
  // matching hand-counted key list. Adding, removing, or reordering a
  // section is now a one-line change here instead of needing to keep the
  // markup, the initial open/closed state, and openHidePanels() all in sync.
  //
  // `schema`/`schemaKind` say how to check "is this section's required data
  // filled in", read straight from the backend's OpenAPI schema (see
  // $lib/utils/schemaValidation.ts) rather than a second hand-maintained
  // list of required fields that could drift from support/base_models.py.
  interface PanelSection {
    key: string;
    label: string;
    icon: Component;
    component: Component;
    schema: string;
    schemaKind: 'object' | 'array';
    field: keyof ModelData;
    /** "In use" test for optional object sections that are always present (see sectionStatus). */
    isUsed?: (data: never) => boolean;
    /** Extra completeness check beyond the schema's required fields (see sectionStatus). */
    isReady?: (data: never) => boolean;
    visible?: () => boolean;
  }

  interface PanelGroup {
    key: string;
    label: string;
    sections: PanelSection[];
  }

  // Grouped instead of one flat 14-item list: related settings are easier
  // to scan for and find when they're under a heading, and it cuts down how
  // much a user has to scroll past to reach e.g. "Solver".
  const PANEL_GROUPS: PanelGroup[] = [
    {
      key: 'geometry',
      label: 'Geometry',
      sections: [
        {
          key: 'model',
          label: 'Model',
          icon: Box as unknown as Component,
          component: ModelSettings,
          schema: 'Model',
          schemaKind: 'object',
          field: 'model',
          // An uploaded-mesh model is only complete once the mesh is there.
          isReady: (m: Model) => m.meshSource !== 'upload' || !!m.meshFile
        },
        {
          key: 'discretization',
          label: 'Discretization',
          icon: Grid3x3 as unknown as Component,
          component: DiscretizationSettings,
          schema: 'Discretization',
          schemaKind: 'object',
          field: 'discretization'
        },
        {
          key: 'blocks',
          label: 'Blocks',
          icon: Grid2x2 as unknown as Component,
          component: BlocksSettings,
          schema: 'Block',
          schemaKind: 'array',
          field: 'blocks'
        }
      ]
    },
    {
      key: 'physics',
      label: 'Physics',
      sections: [
        {
          key: 'material',
          label: 'Material',
          icon: Wrench as unknown as Component,
          component: MaterialSettings,
          schema: 'Material',
          schemaKind: 'array',
          field: 'materials'
        },
        {
          key: 'thermal',
          label: 'Thermal',
          icon: Flame as unknown as Component,
          component: ThermalSettings,
          schema: 'ThermalModel',
          schemaKind: 'array',
          field: 'thermal'
        },
        {
          key: 'additive',
          label: 'Additive',
          icon: Layers as unknown as Component,
          component: AdditiveSettings,
          schema: 'AdditiveModel',
          schemaKind: 'array',
          field: 'additive'
        },
        {
          key: 'damage',
          label: 'Damage Models',
          icon: Scissors as unknown as Component,
          component: DamageSettings,
          schema: 'Damage',
          schemaKind: 'array',
          field: 'damages'
        },
        {
          key: 'contact',
          label: 'Contact',
          icon: Boxes as unknown as Component,
          component: ContactSettings,
          schema: 'Contact',
          schemaKind: 'object',
          field: 'contact',
          isUsed: (contact: Contact) => !!contact.contactModels?.length
        }
      ]
    },
    {
      key: 'simulation',
      label: 'Simulation',
      sections: [
        {
          key: 'boundaryConditions',
          label: 'Boundary Conditions',
          icon: Waypoints as unknown as Component,
          component: BoundaryConditionsSettings,
          schema: 'BoundaryConditions',
          schemaKind: 'object',
          field: 'boundaryConditions'
        },
        {
          key: 'bondFilters',
          label: 'Bond Filters',
          icon: Filter as unknown as Component,
          component: BondFilterSettings,
          schema: 'BondFilters',
          schemaKind: 'array',
          field: 'bondFilters'
        },
        {
          key: 'output',
          label: 'Output',
          icon: LogOut as unknown as Component,
          component: OutputSettings,
          schema: 'Output',
          schemaKind: 'array',
          field: 'outputs'
        },
        {
          key: 'solver',
          label: 'Solver',
          icon: Calculator as unknown as Component,
          component: SolverSettings,
          schema: 'Solver',
          schemaKind: 'array',
          field: 'solvers'
        },
        {
          key: 'deviations',
          label: 'Deviations',
          icon: BarChart3 as unknown as Component,
          component: DeviationsSettings,
          schema: 'Deviations',
          schemaKind: 'object',
          field: 'deviations',
          isUsed: (deviations: Deviations) => deviations.enabled
        }
      ]
    }
  ];

  const ALL_SECTION_KEYS = PANEL_GROUPS.flatMap((g) => g.sections.map((s) => s.key));

  // scrollable=true (default, desktop/tablet inside the resizable-feeling
  // flex pane): this component owns its own bounded scroll region and fills
  // whatever height its flex parent gives it.
  // scrollable=false (mobile tab, see perihub/+page.svelte): renders inline
  // instead, since on mobile the *tab panel* scrolls the whole column -
  // nesting another independently-scrolling region inside that produces a
  // scroll-within-scroll that's awkward on touch.
  let { scrollable = true }: { scrollable?: boolean } = $props();

  // Keyed by section key instead of array index, so state survives
  // PANEL_GROUPS being reordered/extended and can't silently drift out of
  // sync with the number of panels.
  let openPanels = $state<string[]>([]);

  const panelGroups = $derived(
    PANEL_GROUPS.map((group) => ({
      ...group,
      sections: group.sections
        .filter((section) => !section.visible || section.visible())
        .map((section) => ({
          ...section,
          status: sectionStatus(
            section.field,
            section.schema,
            section.schemaKind,
            modelStore.modelData[section.field],
            section.isUsed,
            section.isReady
          )
        }))
    }))
      .filter((group) => group.sections.length > 0)
      .map((group) => ({
        ...group,
        completeCount: group.sections.filter((s) => s.status === 'complete').length,
        usedCount: group.sections.filter((s) => s.status !== 'unused').length
      }))
  );

  $effect(() => {
    viewStore.setupComplete = panelGroups.every((g) => g.completeCount === g.usedCount);
  });

  onMount(() => {
    const stored = localStorage.getItem('openPanels');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.every((v) => typeof v === 'string')) {
          openPanels = parsed;
        } else {
          // Legacy positional boolean-array format from before this
          // rewrite - can't be reliably mapped onto named keys, so drop it
          // rather than risk showing the wrong panels open.
          localStorage.removeItem('openPanels');
        }
      } catch {
        localStorage.removeItem('openPanels');
      }
    }

    const openHidePanels = () => {
      openPanels = openPanels.length > 0 ? [] : ALL_SECTION_KEYS;
    };
    bus.on('openHidePanels', openHidePanels);
    return () => bus.off('openHidePanels', openHidePanels);
  });

  $effect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('openPanels', JSON.stringify(openPanels));
    }
  });
</script>

<div class={scrollable ? 'h-full overflow-y-auto' : ''}>
  <Accordion.Root type="multiple" bind:value={openPanels}>
    {#each panelGroups as group (group.key)}
      <div
        class="border-border bg-muted text-muted-foreground sticky top-0 z-10 flex items-center border-b px-4 py-1.5 text-xs font-semibold tracking-wide uppercase"
      >
        <span class="flex-1">{group.label}</span>
        <span
          class="font-normal normal-case tabular-nums {group.completeCount === group.usedCount
            ? 'text-success'
            : ''}"
          title="Used sections with all required fields filled in (unused optional sections not counted)"
        >
          {group.completeCount}/{group.usedCount} complete
        </span>
      </div>
      {#each group.sections as section (section.key)}
        <AccordionItem
          value={section.key}
          label={section.label}
          icon={section.icon}
          status={section.status}
        >
          <section.component />
        </AccordionItem>
      {/each}
    {/each}
  </Accordion.Root>
</div>
