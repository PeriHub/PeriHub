<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <div class="row my-row">
      <q-toggle class="my-toggle" v-model="solver.matEnabled" :label="solverKeys.matEnabled" standout dense></q-toggle>
      <q-toggle class="my-toggle" v-model="solver.damEnabled" :label="solverKeys.damEnabled" standout dense></q-toggle>
      <q-toggle class="my-toggle" v-model="solver.tempEnabled" :label="solverKeys.tempEnabled" standout
        dense></q-toggle>
      <q-input class="my-input" v-model="solver.initialTime" :rules="[rules.required, rules.name]"
        :label="solverKeys.initialTime" standout dense></q-input>
      <q-input class="my-input" v-model="solver.finalTime" :rules="[rules.required, rules.name]"
        :label="solverKeys.finalTime" standout dense></q-input>
      <q-input class="my-input" v-model="solver.fixedDt"
        v-show="solver.solvertype == 'Implicit' | solver.solvertype == 'Verlet'" :rules="[rules.required, rules.name]"
        :label="solverKeys.fixedDt" standout dense></q-input>
    </div>
    <div class="row my-row">
      <q-select class="my-input" :options="solvertype" v-model="solver.solvertype" :label="solverKeys.solvertype"
        standout dense></q-select>
      <q-input class="my-input" v-model="solver.safetyFactor" :rules="[rules.required, rules.name]"
        :label="solverKeys.safetyFactor" standout dense></q-input>
      <q-input class="my-input" v-model="solver.numericalDamping" :rules="[rules.required, rules.name]"
        :label="solverKeys.numericalDamping" standout dense></q-input>
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
    <div class="row my-row" v-show="solver.solvertype == 'Verlet'">
      <q-toggle class="my-toggle" v-model="solver.adaptivetimeStepping" :label="solverKeys.adaptivetimeStepping"
        standout dense></q-toggle>
      <q-toggle class="my-toggle" v-model="solver.calculateCauchy" :label="solverKeys.calculateCauchy" standout
        dense></q-toggle>
      <q-toggle class="my-toggle" v-model="solver.calculateVonMises" :label="solverKeys.calculateVonMises" standout
        dense></q-toggle>
      <q-toggle class="my-toggle" v-model="solver.calculateStrain" :label="solverKeys.calculateStrain" standout
        dense></q-toggle>
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
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { inject } from 'vue'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'SolverSettings',
  setup() {
    const store = useModelStore();
    const solver = computed(() => store.modelData.solver)
    const job = computed(() => store.modelData.job)
    const bus = inject('bus')
    return {
      store,
      solver,
      job,
      rules,
      bus
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
        // dispEnabled: 'Solve For Displacement',
        matEnabled: 'Material Models',
        damEnabled: 'Damage Models',
        tempEnabled: 'Thermal Models',
        verbose: 'Verbose',
        initialTime: 'Initial Time',
        finalTime: 'Final Time',
        solvertype: 'Solvertype',
        fixedDt: 'Fixed dt',
        safetyFactor: 'Safety Factor',
        numericalDamping: 'Numerical Damping',
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
  }
})
</script>
