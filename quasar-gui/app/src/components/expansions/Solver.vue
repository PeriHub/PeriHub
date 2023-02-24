<template>
    <q-list bordered class="rounded-borders">
        <q-expansion-item
            expand-separator
            icon="fas fa-calculator"
            label="Solver"
            caption="John Doe"
        >
            <div class="row my-row">
                <q-input 
                    class="my-input"
                    v-model="solver.initialTime"
                    :rules="[rules.required, rules.name]"
                    :label="solverKeys.initialTime"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.finalTime"
                    :rules="[rules.required, rules.name]"
                    :label="solverKeys.finalTime"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.fixedDt"
                    v-show="solver.solvertype=='Implicit' | solver.solvertype=='Verlet'"
                    :rules="[rules.required, rules.name]"
                    :label="solverKeys.fixedDt"
                    outlined
                    dense
                ></q-input>
                <q-toggle
                    class="my-toggle"
                    v-model="solver.verbose"
                    :label="solverKeys.verbose"
                    outlined
                    dense
                ></q-toggle>
            </div>
            <div class="row my-row">
                <q-select 
                    class="my-input"
                    :options="solvertype"
                    v-model="solver.solvertype"
                    :label="solverKeys.solvertype"
                    outlined
                    dense
                ></q-select>
                <q-input 
                    class="my-input"
                    v-model="solver.safetyFactor"
                    :rules="[rules.required, rules.name]"
                    :label="solverKeys.safetyFactor"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.numericalDamping"
                    :rules="[rules.required, rules.name]"
                    :label="solverKeys.numericalDamping"
                    outlined
                    dense
                ></q-input>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='NOXQuasiStatic'">
                <q-select 
                    class="my-input"
                    :options="peridgimPreconditioner"
                    v-model="solver.peridgimPreconditioner"
                    :label="solverKeys.peridgimPreconditioner"
                    outlined
                    dense
                ></q-select>
                <q-select 
                    class="my-input"
                    :options="nonlinearSolver"
                    v-model="solver.nonlinearSolver"
                    :label="solverKeys.nonlinearSolver"
                    outlined
                    dense
                ></q-select>
                <q-input 
                    class="my-input"
                    v-model="solver.numberOfLoadSteps"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.numberOfLoadSteps"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.maxSolverIterations"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.maxSolverIterations"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.relativeTolerance"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.relativeTolerance"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.maxAgeOfPrec"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.maxAgeOfPrec"
                    outlined
                    dense
                ></q-input>
                <q-select 
                    class="my-input"
                    :options="directionMethod"
                    v-model="solver.directionMethod"
                    :label="solverKeys.directionMethod"
                    outlined
                    dense
                ></q-select>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='NOXQuasiStatic'">
                <q-select 
                    class="my-input"
                    :options="jacobianOperator"
                    v-model="solver.newton.jacobianOperator"
                    :label="solverKeys.newton.jacobianOperator"
                    outlined
                    dense
                ></q-select>
                <q-select 
                    class="my-input"
                    :options="preconditioner"
                    v-model="solver.newton.preconditioner"
                    :label="solverKeys.newton.preconditioner"
                    outlined
                    dense
                ></q-select>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='NOXQuasiStatic'">
                <q-select 
                    class="my-input"
                    :options="lineSearchMethod"
                    v-model="solver.lineSearchMethod"
                    :label="solverKeys.lineSearchMethod"
                    outlined
                    dense
                ></q-select>
                <q-toggle
                    class="my-toggle"
                    v-model="solver.verletSwitch"
                    :label="solverKeys.verletSwitch"
                    outlined
                    dense
                ></q-toggle>
            </div>
            <div class="row my-row" v-show="solver.verletSwitch & solver.solvertype=='NOXQuasiStatic'">
                <q-input 
                    class="my-input"
                    v-model="solver.verlet.safetyFactor"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.verlet.safetyFactor"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.verlet.numericalDamping"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.verlet.numericalDamping"
                    outlined
                    dense
                ></q-input>
                <q-input 
                    class="my-input"
                    v-model="solver.verlet.outputFrequency"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.verlet.outputFrequency"
                    outlined
                    dense
                ></q-input>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='Verlet'">
                <q-toggle
                    class="my-toggle"
                    v-model="solver.adaptivetimeStepping"
                    :label="solverKeys.adaptivetimeStepping"
                    outlined
                    dense
                ></q-toggle>
            </div>
            <div class="row my-row">
                <q-toggle
                    class="my-toggle"
                    v-model="solver.stopAfterDamageInitation"
                    :label="solverKeys.stopAfterDamageInitation"
                    outlined
                    dense
                ></q-toggle>
                <q-input v-show="solver.stopAfterDamageInitation"
                    class="my-input"
                    v-model="solver.endStepAfterDamagey"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.endStepAfterDamagey"
                    outlined
                    dense
                ></q-input>
                <q-toggle
                    class="my-toggle"
                    v-model="solver.stopBeforeDamageInitation"
                    :label="solverKeys.stopBeforeDamageInitation"
                    outlined
                    dense
                ></q-toggle>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='Verlet' & solver.adaptivetimeStepping">
                <q-input
                    class="my-input"
                    v-model="solver.adapt.stableStepDifference"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.adapt.stableStepDifference"
                    outlined
                    dense
                ></q-input>
                <q-input
                    class="my-input"
                    v-model="solver.adapt.maximumBondDifference"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.adapt.maximumBondDifference"
                    outlined
                    dense
                ></q-input>
                <q-input
                    class="my-input"
                    v-model="solver.adapt.stableBondDifference"
                    :rules="[rules.required, rules.int]"
                    :label="solverKeys.adapt.stableBondDifference"
                    outlined
                    dense
                ></q-input>
            </div>
            <div class="row my-row" v-show="solver.solvertype=='Verlet' & solver.adaptivetimeStepping">
                <q-select 
                    class="my-input"
                    :options="filetype"
                    v-model="solver.filetype"
                    v-show="job.cluster=='Cara'"
                    :label="solverKeys.filetype"
                    outlined
                    dense
                ></q-select>
            </div>
        </q-expansion-item>
    </q-list>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
  
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
                solvertype: ["Verlet", "NOXQuasiStatic"],
                peridgimPreconditioner: ["Full Tangent", "Block 3x3", "None"],
                nonlinearSolver: ["Line Search Based"],
                directionMethod: ["Newton", "NonlinearCG"],
                jacobianOperator: ["Matrix-Free", ""],
                preconditioner: ["User Defined", "None"],
                lineSearchMethod: ["Polynomial"],
                filetype: ["yaml", "xml"],
                solverKeys: {
                    verbose: "Verbose",
                    initialTime: "Initial Time",
                    finalTime: "Final Time",
                    solvertype: "Solvertype",
                    fixedDt: "Fixed dt",
                    safetyFactor: "Safety Factor",
                    numericalDamping: "Numerical Damping",
                    peridgimPreconditioner: "Peridgim Preconditioner",
                    nonlinearSolver: "Nonlinear Solver",
                    numberOfLoadSteps: "Number of Load Steps",
                    maxSolverIterations: "Max Solver Iterations",
                    relativeTolerance: "Relative Tolerance",
                    maxAgeOfPrec: "Max Age Of Prec",
                    directionMethod: "Direction Method",
                    newton: {
                    jacobianOperator: "Jacobian Operator",
                    preconditioner: "Preconditioner",
                    },
                    lineSearchMethod: "Line Search Method",
                    verletSwitch: "Switch to Verlet",
                    verlet: {
                    safetyFactor: "Safety Factor",
                    numericalDamping: "Numerical Damping",
                    outputFrequency: "Output Frequency",
                    },
                    stopAfterDamageInitation: "Stop after damage initation",
                    endStepAfterDamage: "End step after damage",
                    stopBeforeDamageInitation: "Stop before damage initation",
                    adaptivetimeStepping: "Adaptive Time Stepping",
                    adapt: {
                    stableStepDifference: "Stable Step Difference",
                    maximumBondDifference: "Maximum Bond Difference",
                    stableBondDifference: "Stable Bond Difference",
                    },
                },
            };
        },
        methods: {
        }
    })
</script>
<style>
.my-title {
    margin-top: 10px;
    margin-bottom: 0px;
    margin-left: 10px;
}
.my-row {
    min-height: 50px;
}
.my-input {
    margin-left: 10px;
}
.my-toggle {
    height: 40px;
    margin: 10px;
}
</style>