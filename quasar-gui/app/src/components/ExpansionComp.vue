<template>
    <div>
        <ModelSettings></ModelSettings>
        <MaterialSettings></MaterialSettings>
        <DamageSettings></DamageSettings>
        <BlocksSettings></BlocksSettings>
        <ContactSettings></ContactSettings>
        <BoundaryConditionsSettings></BoundaryConditionsSettings>
        <BondFilterSettings></BondFilterSettings>
        <OutputSettings></OutputSettings>
        <SolverSettings></SolverSettings>
        <JobSettings></JobSettings>
    </div>
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