<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { Solver } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import SchemaForm from '$lib/components/SchemaForm.svelte';

  const solvers = $derived(modelStore.modelData.solvers ?? []);

  function addSolver() {
    const len = solvers.length;
    const newItem = structuredClone($state.snapshot(solvers[len - 1])) as Solver;
    newItem.solverId = len + 1;
    newItem.stepId = len + 1;
    solvers.push(newItem);
  }

  function removeSolver(index: number) {
    solvers.splice(index, 1);
    solvers.forEach((s, i) => (s.solverId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  {#each solvers as solver, index (solver.solverId ?? index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <div class="flex items-center justify-between">
        <h4 class="font-medium">Solver {solver.solverId}</h4>
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

      <div class="space-y-1">
        <Label for={`sv-name-${index}`}>Solver Name</Label>
        <Input id={`sv-name-${index}`} bind:value={solver.name} />
      </div>

      <!--
        Every plain scalar field of Solver (solvertype, the 4 model-toggles,
        initial/final time, max. damage) is rendered here from the schema's
        yaml_field(...) metadata - see support/base_models.py. Adding a new
        simple Solver field only means editing that model; this component
        picks it up automatically. additionalTime stays hand-written just
        below since it has a real structural rule (only meaningful for
        solvers after the first) that a generic renderer shouldn't guess at.
      -->
      <SchemaForm schemaName="Solver" data={solver} group="Solver" />

      {#if solver.stepId !== 1}
        <div class="max-w-xs space-y-1">
          <Label for={`sv-add-${index}`}>Additional Time</Label>
          <Input id={`sv-add-${index}`} type="number" bind:value={solver.additionalTime} />
        </div>
      {/if}

      {#if solver.solvertype === 'Verlet' && solver.verlet != null}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`sv-damp-${index}`}>Numerical Damping</Label>
            <Input
              id={`sv-damp-${index}`}
              type="number"
              bind:value={solver.verlet.numericalDamping}
              clearable
            />
          </div>
          <!--
            fixedDt/safetyFactor/adaptivetimeStepping/calculateCauchy/
            calculateVonMises/calculateStrain, all Verlet-only fields on the
            Solver schema itself (ui_group: "Verlet"). Numerical Damping above
            stays hand-written because it lives on the separate nested Verlet
            sub-model (solver.verlet), not on Solver directly - SchemaForm
            only understands one schema/data pair at a time.
          -->
          <SchemaForm schemaName="Solver" data={solver} group="Verlet" />
        </div>
      {/if}

      {#if solver.solvertype === 'Static' && solver.static != null}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`sv-steps-${index}`}>Number of Steps</Label>
            <Input
              id={`sv-steps-${index}`}
              type="number"
              bind:value={solver.static.numberOfSteps}
            />
          </div>
          <div class="space-y-1">
            <Label for={`sv-iters-${index}`}>Maximum number of iterations</Label>
            <Input
              id={`sv-iters-${index}`}
              type="number"
              bind:value={solver.static.maximumNumberOfIterations}
            />
          </div>
          <Toggle bind:checked={solver.static.showSolverIteration} label="Show Solver Iteration" />
          <div class="space-y-1">
            <Label for={`sv-restol-${index}`}>Residual Tolerance</Label>
            <Input
              id={`sv-restol-${index}`}
              type="number"
              bind:value={solver.static.residualTolerance}
            />
          </div>
          <div class="space-y-1">
            <Label for={`sv-soltol-${index}`}>Solution Tolerance</Label>
            <Input
              id={`sv-soltol-${index}`}
              type="number"
              bind:value={solver.static.solutionTolerance}
            />
          </div>
          <div class="space-y-1">
            <Label for={`sv-resscale-${index}`}>Residual Scaling</Label>
            <Input
              id={`sv-resscale-${index}`}
              type="number"
              bind:value={solver.static.residualScaling}
            />
          </div>
          <div class="space-y-1">
            <Label for={`sv-m-${index}`}>m</Label>
            <Input id={`sv-m-${index}`} type="number" bind:value={solver.static.m} />
          </div>
        </div>
      {/if}
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addSolver}>
    <Plus class="h-4 w-4" /> Add Solver
  </Button>
</div>
