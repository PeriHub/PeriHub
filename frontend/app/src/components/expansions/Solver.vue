<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <q-list v-for="solver, index in solvers" :key="solver.solverId" style="padding: 0px">
      <div
        v-bind:style="(solver.solverId! % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
        <h4 class="my-title">Solver {{ solver.solverId }}</h4>
        <div class="row my-row">
          <q-input class="my-input" v-model="solver.name" :rules="[rules.required, rules.name]" :label="solverKeys.name"
            standout dense></q-input>
          <q-space></q-space>
          <q-btn v-if="solvers.length > 1" flat icon="fas fa-trash-alt" @click="removeSolver(index)">
            <q-tooltip>
              Remove Solver
            </q-tooltip>
          </q-btn>
        </div>
        <div class="row my-row">
          <q-toggle class="my-toggle" v-model="solver.matEnabled" :label="solverKeys.matEnabled" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.damEnabled" :label="solverKeys.damEnabled" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.tempEnabled" :label="solverKeys.tempEnabled" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.addEnabled" :label="solverKeys.addEnabled" standout
            dense></q-toggle>
          <q-input class="my-input" v-model="solver.initialTime" clearable :rules="[rules.float]"
            :label="solverKeys.initialTime" standout dense></q-input>
          <q-input class="my-input" v-model="solver.finalTime" clearable :rules="[rules.float]"
            :label="solverKeys.finalTime" standout dense></q-input>
          <q-input class="my-input" v-if="solver.stepId != 1" v-model="solver.additionalTime" clearable
            :rules="[rules.float]" :label="solverKeys.additionalTime" standout dense></q-input>
          <q-input class="my-input" v-model="solver.fixedDt"
            v-show="solver.solvertype == 'Implicit' | solver.solvertype == 'Verlet'" :rules="[rules.posFloat]"
            :label="solverKeys.fixedDt" standout dense clearable></q-input>
        </div>
        <div class="row my-row">
          <q-select class="my-input" :options="solvertype" v-model="solver.solvertype" :label="solverKeys.solvertype"
            standout dense></q-select>
          <q-input class="my-input" v-model="solver.safetyFactor" :rules="[rules.required, rules.posFloat]"
            :label="solverKeys.safetyFactor" standout dense></q-input>
        </div>
        <!-- <div class="row my-row" v-show="solver.solvertype == 'NOXQuasiStatic'">
            <q-select class="my-input" :options="peridgimPreconditioner" v-model="solver.peridgimPreconditioner"
                :label="solverKeys.peridgimPreconditioner" standout dense></q-select>
            <q-select class="my-input" :options="nonlinearSolver" v-model="solver.nonlinearSolver"
                :label="solverKeys.nonlinearSolver" standout dense></q-select>
            <q-input class="my-input" v-model="solver.numberOfLoadSteps" :rules="[rules.required, rules.int]"
                :label="solverKeys.numberOfLoadSteps" standout dense></q-input>
            <q-input class="my-input" v-model="solver.maxSolverIterations" :rules="[rules.required, rules.int]"
                :label="solverKeys.maxSolverIterations" standout dense></q-input>
            <q-input class="my-input" v-model="solver.relativeTolerance" :rules="[rules.required, rules.int]"
                :label="solverKeys.relativeTolerance" standout dense></q-input>
            <q-input class="my-input" v-model="solver.maxAgeOfPrec" :rules="[rules.required, rules.int]"
                :label="solverKeys.maxAgeOfPrec" standout dense></q-input>
            <q-select class="my-input" :options="directionMethod" v-model="solver.directionMethod"
                :label="solverKeys.directionMethod" standout dense></q-select>
        </div>
        <div class="row my-row" v-show="solver.solvertype == 'NOXQuasiStatic'">
            <q-select class="my-input" :options="jacobianOperator" v-model="solver.newton.jacobianOperator"
                :label="solverKeys.newton.jacobianOperator" standout dense></q-select>
            <q-select class="my-input" :options="preconditioner" v-model="solver.newton.preconditioner"
                :label="solverKeys.newton.preconditioner" standout dense></q-select>
        </div>
        <div class="row my-row" v-show="solver.solvertype == 'NOXQuasiStatic'">
            <q-select class="my-input" :options="lineSearchMethod" v-model="solver.lineSearchMethod"
                :label="solverKeys.lineSearchMethod" standout dense></q-select>
            <q-toggle class="my-toggle" v-model="solver.verletSwitch" :label="solverKeys.verletSwitch" standout
                dense></q-toggle>
        </div>
        <div class="row my-row" v-show="solver.verletSwitch & solver.solvertype == 'NOXQuasiStatic'">
            <q-input class="my-input" v-model="solver.verlet.safetyFactor" :rules="[rules.required, rules.int]"
                :label="solverKeys.verlet.safetyFactor" standout dense></q-input>
            <q-input class="my-input" v-model="solver.verlet.numericalDamping" :rules="[rules.required, rules.int]"
                :label="solverKeys.verlet.numericalDamping" standout dense></q-input>
            <q-input class="my-input" v-model="solver.verlet.outputFrequency" :rules="[rules.required, rules.int]"
                :label="solverKeys.verlet.outputFrequency" standout dense></q-input>
        </div> -->
        <div class="row my-row" v-show="solver.solvertype == 'Verlet' && solver.verlet != null">
          <q-input class="my-input" v-model="solver.verlet.numericalDamping" :rules="[rules.required, rules.posFloat]"
            :label="solverKeys.verlet.numericalDamping" standout dense></q-input>
          <q-toggle class="my-toggle" v-model="solver.adaptivetimeStepping" :label="solverKeys.adaptivetimeStepping"
            standout dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.calculateCauchy" :label="solverKeys.calculateCauchy" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.calculateVonMises" :label="solverKeys.calculateVonMises" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="solver.calculateStrain" :label="solverKeys.calculateStrain" standout
            dense></q-toggle>
        </div>
        <div class="row my-row" v-if="solver.solvertype == 'Static' && solver.static != null">
          <q-input class="my-input" v-model="solver.static.numberOfSteps" :rules="[rules.required, rules.int]"
            :label="solverKeys.static.numberOfSteps" standout dense></q-input>
          <q-input class="my-input" v-model="solver.static.maximumNumberOfIterations"
            :rules="[rules.required, rules.int]" :label="solverKeys.static.maximumNumberOfIterations" standout
            dense></q-input>
          <q-toggle class="my-toggle" v-model="solver.static.showSolverIteration"
            :label="solverKeys.static.showSolverIteration" standout dense></q-toggle>
          <q-input class="my-input" v-model="solver.static.residualTolerance" :rules="[rules.required, rules.posFloat]"
            :label="solverKeys.static.residualTolerance" standout dense></q-input>
          <q-input class="my-input" v-model="solver.static.solutionTolerance" :rules="[rules.required, rules.posFloat]"
            :label="solverKeys.static.solutionTolerance" standout dense></q-input>
          <!-- <q-input class="my-input" v-model="solver.static.linearStartValue" :rules="[rules.required, rules.name]"
            :label="solverKeys.static.linearStartValue" standout dense></q-input> -->
          <q-input class="my-input" v-model="solver.static.residualScaling" :rules="[rules.required, rules.posFloat]"
            :label="solverKeys.static.residualScaling" standout dense></q-input>
          <q-input class="my-input" v-model="solver.static.m" :rules="[rules.required, rules.int]"
            :label="solverKeys.static.m" standout dense></q-input>

        </div>
        <!-- <div class="row my-row">
            <q-toggle class="my-toggle" v-model="solver.stopAfterDamageInitation"
                :label="solverKeys.stopAfterDamageInitation" standout dense></q-toggle>
            <q-input v-show="solver.stopAfterDamageInitation" class="my-input" v-model="solver.endStepAfterDamagey"
                :rules="[rules.required, rules.int]" :label="solverKeys.endStepAfterDamagey" standout dense></q-input>
            <q-toggle class="my-toggle" v-model="solver.stopBeforeDamageInitation"
                :label="solverKeys.stopBeforeDamageInitation" standout dense></q-toggle>
        </div>
        <div class="row my-row">
            <q-toggle class="my-toggle" v-model="solver.stopAfterCertainDamage" :label="solverKeys.stopAfterCertainDamage"
                standout dense></q-toggle>
            <q-input v-show="solver.stopAfterCertainDamage" class="my-input" v-model="solver.maxDamageValue"
                :rules="[rules.required, rules.float]" :label="solverKeys.maxDamageValue" standout dense></q-input>
        </div>
        <div class="row my-row" v-show="solver.solvertype == 'Verlet' & solver.adaptivetimeStepping">
            <q-input class="my-input" v-model="solver.adapt.stableStepDifference" :rules="[rules.required, rules.int]"
                :label="solverKeys.adapt.stableStepDifference" standout dense></q-input>
            <q-input class="my-input" v-model="solver.adapt.maximumBondDifference" :rules="[rules.required, rules.int]"
                :label="solverKeys.adapt.maximumBondDifference" standout dense></q-input>
            <q-input class="my-input" v-model="solver.adapt.stableBondDifference" :rules="[rules.required, rules.int]"
                :label="solverKeys.adapt.stableBondDifference" standout dense></q-input>
        </div>
        <div class="row my-row" v-show="solver.solvertype == 'Verlet' & solver.adaptivetimeStepping">
            <q-select class="my-input" :options="filetype" v-model="solver.filetype" v-show="job.cluster"
                :label="solverKeys.filetype" standout dense></q-select>
        </div> -->
      </div>
      <q-separator></q-separator>
    </q-list>
    <q-btn flat icon="fas fa-plus" @click="addSolver">
      <q-tooltip>
        Add Solver
      </q-tooltip>
    </q-btn>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { Solver } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'SolverSettings',
  setup() {
    const store = useModelStore();
    const solvers = computed(() => store.modelData.solvers)
    const job = computed(() => store.modelData.job)
    return {
      store,
      solvers,
      job,
      rules
    }
  },
  created() {
  },
  data() {
    return {
      solvertype: ['Verlet'],
      // solvertype: ['Verlet', 'NOXQuasiStatic'],
      peridgimPreconditioner: ['Full Tangent', 'Block 3x3', 'None'],
      nonlinearSolver: ['Line Search Based'],
      directionMethod: ['Newton', 'NonlinearCG'],
      jacobianOperator: ['Matrix-Free', ''],
      preconditioner: ['User Defined', 'None'],
      lineSearchMethod: ['Polynomial'],
      solverKeys: {
        name: 'Solver Name',
        // dispEnabled: 'Solve For Displacement',
        matEnabled: 'Material Models',
        damEnabled: 'Damage Models',
        tempEnabled: 'Thermal Models',
        addEnabled: 'Additive Models',
        verbose: 'Verbose',
        initialTime: 'Initial Time',
        finalTime: 'Final Time',
        additionalTime: 'Additional Time',
        solvertype: 'Solvertype',
        fixedDt: 'Fixed dt',
        safetyFactor: 'Safety Factor',
        peridgimPreconditioner: 'Peridgim Preconditioner',
        nonlinearSolver: 'Nonlinear Solver',
        numberOfLoadSteps: 'Number of Load Steps',
        maxSolverIterations: 'Max Solver Iterations',
        relativeTolerance: 'Relative Tolerance',
        maxAgeOfPrec: 'Max Age Of Prec',
        directionMethod: 'Direction Method',
        newton: {
          jacobianOperator: 'Jacobian Operator',
          preconditioner: 'Preconditioner',
        },
        lineSearchMethod: 'Line Search Method',
        verletSwitch: 'Switch to Verlet',
        verlet: {
          safetyFactor: 'Safety Factor',
          numericalDamping: 'Numerical Damping',
          outputFrequency: 'Output Frequency',
        },
        static: {
          numberOfSteps: 'Number of Steps',
          maximumNumberOfIterations: 'Maximum number of iterations',
          showSolverIteration: 'Show Solver Iteration',
          residualTolerance: 'Residual Tolerance',
          solutionTolerance: 'Solution Tolerance',
          linearStartValue: 'Linear Start Value',
          residualScaling: 'Residual Scaling',
          m: 'm'
        },
        stopAfterDamageInitation: 'Stop after damage initation',
        endStepAfterDamage: 'End step after damage',
        stopBeforeDamageInitation: 'Stop before damage initation',
        stopAfterCertainDamage: 'Stop after certain damage value',
        maxDamageValue: 'Max. damage value',
        adaptivetimeStepping: 'Adaptive Time Stepping',
        adapt: {
          stableStepDifference: 'Stable Step Difference',
          maximumBondDifference: 'Maximum Bond Difference',
          stableBondDifference: 'Stable Bond Difference',
        },
        calculateCauchy: 'Calculate Cauchy',
        calculateVonMises: 'Calculate von Mises',
        calculateStrain: 'Calculate Strain',
      },
    };
  },
  methods: {
    addSolver() {
      const len = this.solvers.length;
      const newItem = structuredClone(this.solvers[len - 1]) as Solver
      newItem.solverId = len + 1
      newItem.stepId = len + 1
      this.solvers.push(newItem);
    },
    removeSolver(index) {
      this.solvers.splice(index, 1);
      this.solvers.forEach((solver, i) => {
        solver.solverId = i + 1
      })
    },
  }
})
</script>
