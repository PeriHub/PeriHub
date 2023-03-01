<template>
    <q-scroll-area style="height: calc(100vh - 183px);">
        <q-list bordered class="rounded-borders">
            <q-expansion-item
                expand-separator
                icon="fas fa-cube"
                label="Model"
                caption="John Doe"
            >
                <ModelSettings></ModelSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-toolbox"
            label="Material"
                caption="John Doe"
            >
                <MaterialSettings></MaterialSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-cut"
            label="Damage Models"
                caption="John Doe"
            >
                <DamageSettings></DamageSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-th"
            label="Blocks"
                caption="John Doe"
            >
                <BlocksSettings></BlocksSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-boxes-stacked"
            label="Contact"
                caption="John Doe"
            >
                <ContactSettings></ContactSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-project-diagram"
            label="Boundary Conditions"
                caption="John Doe"
            >
                <BoundaryConditionsSettings></BoundaryConditionsSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-filter"
            label="Bond Filters"
                caption="John Doe"
            >
                <BondFilterSettings></BondFilterSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-sign-out-alt"
                label="Output"
                caption="John Doe"
            >
                <OutputSettings></OutputSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
                icon="fas fa-calculator"
                label="Solver"
                caption="John Doe"
            >
                <SolverSettings></SolverSettings>
            </q-expansion-item>
            <q-expansion-item
                expand-separator
            icon="fas fa-flask"
            label="Job"
                caption="John Doe"
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