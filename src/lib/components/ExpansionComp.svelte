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
    FlaskConical,
    BarChart3
  } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { isObjectSectionComplete, isArraySectionComplete } from '$lib/utils/schemaValidation';
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
  import JobSettings from '$lib/components/expansions/Job.svelte';
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
    dataPath: (modelData: Record<string, unknown>) => unknown;
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
          icon: Box,
          component: ModelSettings,
          schema: 'Model',
          schemaKind: 'object',
          dataPath: (m) => m.model
        },
        {
          key: 'discretization',
          label: 'Discretization',
          icon: Grid3x3,
          component: DiscretizationSettings,
          schema: 'Discretization',
          schemaKind: 'object',
          dataPath: (m) => m.discretization
        },
        {
          key: 'blocks',
          label: 'Blocks',
          icon: Grid2x2,
          component: BlocksSettings,
          schema: 'Block',
          schemaKind: 'array',
          dataPath: (m) => m.blocks
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
          icon: Wrench,
          component: MaterialSettings,
          schema: 'Material',
          schemaKind: 'array',
          dataPath: (m) => m.materials
        },
        {
          key: 'thermal',
          label: 'Thermal',
          icon: Flame,
          component: ThermalSettings,
          schema: 'Thermal',
          schemaKind: 'object',
          dataPath: (m) => m.thermal
        },
        {
          key: 'additive',
          label: 'Additive',
          icon: Layers,
          component: AdditiveSettings,
          schema: 'Additive',
          schemaKind: 'object',
          dataPath: (m) => m.additive
        },
        {
          key: 'damage',
          label: 'Damage Models',
          icon: Scissors,
          component: DamageSettings,
          schema: 'Damage',
          schemaKind: 'array',
          dataPath: (m) => m.damages
        },
        {
          key: 'contact',
          label: 'Contact',
          icon: Boxes,
          component: ContactSettings,
          schema: 'Contact',
          schemaKind: 'object',
          dataPath: (m) => m.contact
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
          icon: Waypoints,
          component: BoundaryConditionsSettings,
          schema: 'BoundaryConditions',
          schemaKind: 'object',
          dataPath: (m) => m.boundaryConditions
        },
        {
          key: 'bondFilters',
          label: 'Bond Filters',
          icon: Filter,
          component: BondFilterSettings,
          schema: 'BondFilters',
          schemaKind: 'array',
          dataPath: (m) => m.bondFilters
        },
        {
          key: 'output',
          label: 'Output',
          icon: LogOut,
          component: OutputSettings,
          schema: 'Output',
          schemaKind: 'array',
          dataPath: (m) => m.outputs
        },
        {
          key: 'solver',
          label: 'Solver',
          icon: Calculator,
          component: SolverSettings,
          schema: 'Solver',
          schemaKind: 'array',
          dataPath: (m) => m.solvers
        },
        {
          key: 'job',
          label: 'Job',
          icon: FlaskConical,
          component: JobSettings,
          schema: 'Job',
          schemaKind: 'object',
          dataPath: (m) => m.job,
          visible: () => defaultStore.cluster !== ''
        },
        {
          key: 'deviations',
          label: 'Deviations',
          icon: BarChart3,
          component: DeviationsSettings,
          schema: 'Deviations',
          schemaKind: 'object',
          dataPath: (m) => m.deviations
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
          complete:
            section.schemaKind === 'array'
              ? isArraySectionComplete(
                  section.schema,
                  section.dataPath(modelStore.modelData as unknown as Record<string, unknown>)
                )
              : isObjectSectionComplete(
                  section.schema,
                  section.dataPath(modelStore.modelData as unknown as Record<string, unknown>)
                )
        }))
    })).filter((group) => group.sections.length > 0)
  );

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
        class="border-border bg-muted/30 text-muted-foreground border-b px-4 py-1.5 text-xs font-semibold tracking-wide uppercase"
      >
        {group.label}
      </div>
      {#each group.sections as section (section.key)}
        <AccordionItem
          value={section.key}
          label={section.label}
          icon={section.icon}
          complete={section.complete}
        >
          <section.component />
        </AccordionItem>
      {/each}
    {/each}
  </Accordion.Root>
</div>
