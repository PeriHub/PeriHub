<template>
    <q-scroll-area style="height: calc(100vh - 185px);">
        <q-list bordered class="rounded-borders">
            <q-expansion-item
                expand-separator
                icon="fas fa-cube"
                label="Model"
            >
                <ModelSettings></ModelSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-toolbox"
                label="Material"
            >
                <MaterialSettings></MaterialSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-cut"
                label="Damage Models"
            >
                <DamageSettings></DamageSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-th"
                label="Blocks"
            >
                <BlocksSettings></BlocksSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-boxes-stacked"
                label="Contact"
            >
                <ContactSettings></ContactSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-project-diagram"
                label="Boundary Conditions"
            >
                <BoundaryConditionsSettings></BoundaryConditionsSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-filter"
                label="Bond Filters"
            >
                <BondFilterSettings></BondFilterSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-sign-out-alt"
                label="Output"
            >
                <OutputSettings></OutputSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-calculator"
                label="Solver"
            >
                <SolverSettings></SolverSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-flask"
                label="Job"
            >
                <JobSettings></JobSettings>
            </q-expansion-item>
        </q-list>
    </q-scroll-area>
</template>

<script>
import { defineComponent } from 'vue'
import ModelSettings from 'components/expansions/Model.vue'
import MaterialSettings from 'components/expansions/Material.vue'
import DamageSettings from 'components/expansions/Damage.vue'
import BlocksSettings from 'components/expansions/Blocks.vue'
import ContactSettings from 'components/expansions/Contact.vue'
import BoundaryConditionsSettings from 'components/expansions/BoundaryConditions.vue'
import BondFilterSettings from 'components/expansions/BondFilters.vue'
import OutputSettings from 'components/expansions/Output.vue'
import SolverSettings from 'components/expansions/Solver.vue'
import JobSettings from 'components/expansions/Job.vue'

export default defineComponent({
    name: "ExpansionComp",
    components: {
        ModelSettings,
        MaterialSettings,
        DamageSettings,
        BlocksSettings,
        ContactSettings,
        BoundaryConditionsSettings,
        BondFilterSettings,
        OutputSettings,
        SolverSettings,
        JobSettings
    },
})
</script>