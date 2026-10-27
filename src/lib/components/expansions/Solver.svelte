<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { Solver } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import { sections, node, solverNames, pick, CUSTOM_KEYS } from '$lib/perilab/schema';

  const solvers = $derived(modelStore.modelData.solvers ?? []);
  // More than one solver is written as a Multistep Solver, whose steps have their own schema (no required times).
  const section = $derived(solvers.length > 1 ? sections.multistepSolver : sections.solver);

  function addSolver() {
    const len = solvers.length;
    const newItem = structuredClone($state.snapshot(solvers[len - 1])) as Solver;
    newItem.solverId = len + 1;
    newItem.stepId = len + 1;
    newItem.name = `Step ${len + 1}`;
    solvers.push(newItem);
  }

  function removeSolver(index: number) {
    solvers.splice(index, 1);
    solvers.forEach((s, i) => (s.solverId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  {#each solvers as solver, index (index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <div class="flex items-center justify-between">
        <h4 class="font-medium">{solver.name ?? `Solver ${solver.solverId}`}</h4>
        {#if solvers.length > 1}
          <Button
            variant="ghost"
            size="icon"
            onclick={() => removeSolver(index)}
            title="Remove Solver"
          >
            <Trash2 class="h-4 w-4" />
          </Button>
        {/if}
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`sv-name-${index}`}>Name</Label>
          <Input id={`sv-name-${index}`} bind:value={solver.name} />
        </div>
        <div class="space-y-1">
          <Label for={`sv-type-${index}`}>Solver</Label>
          <Select id={`sv-type-${index}`} bind:value={solver.solvertype}>
            {#each pick(solverNames(), ['Verlet', 'Static'], solver.solvertype) as name (name)}
              <option value={name}>{name}</option>
            {/each}
          </Select>
        </div>
      </div>

      <SchemaParams
        entry={section}
        values={solver.params!}
        custom={CUSTOM_KEYS.solver}
        solver={solver.solvertype}
        idPrefix={`sv-${index}`}
      />

      <h5 class="text-muted-foreground text-sm font-medium">{solver.solvertype}</h5>
      <SchemaParams
        entry={node([solver.solvertype], section)}
        values={solver.solverOptions!}
        idPrefix={`sv-${index}-opt`}
      />
    </div>
  {/each}

  <AddButton noun="solver" items={solvers} onclick={addSolver} />
</div>
