<template>
    <q-scroll-area style="height: calc(100vh - 185px);">
        <q-list bordered class="rounded-borders">
            <q-expansion-item
                v-model="panel[0]"
                expand-separator
                icon="fas fa-cube"
                label="Model"
            >
                <ModelSettings></ModelSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[1]"
                expand-separator
                icon="fas fa-toolbox"
                label="Material"
            >
                <MaterialSettings></MaterialSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[2]"
                expand-separator
                icon="fas fa-cut"
                label="Damage Models"
            >
                <DamageSettings></DamageSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[3]"
                expand-separator
                icon="fas fa-th"
                label="Blocks"
            >
                <BlocksSettings></BlocksSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[4]"
                expand-separator
                icon="fas fa-boxes-stacked"
                label="Contact"
            >
                <ContactSettings></ContactSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[5]"
                expand-separator
                icon="fas fa-project-diagram"
                label="Boundary Conditions"
            >
                <BoundaryConditionsSettings></BoundaryConditionsSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[6]"
                expand-separator
                icon="fas fa-filter"
                label="Bond Filters"
            >
                <BondFilterSettings></BondFilterSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[7]"
                expand-separator
                icon="fas fa-sign-out-alt"
                label="Output"
            >
                <OutputSettings></OutputSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[8]"
                expand-separator
                icon="fas fa-calculator"
                label="Solver"
            >
                <SolverSettings></SolverSettings>
            </q-expansion-item>
            <q-expansion-item
                v-model="panel[9]"
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
import { defineComponent, inject } from 'vue'
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
    setup() {
        const bus = inject('bus')
        return {
            bus,
        }
    },
    created() {
        this.bus.on('openHidePanels', () => {
            console.log("openHidePanels")
            this.openHidePanels()
        })
    },
    data() {
        return {
            panel: [false,false,false,false,false,false,false,false,false,false],
        }
    },
    methods: {
        openHidePanels() {
            if (this.panel.includes(true)) {
                this.panel = [false,false,false,false,false,false,false,false,false,false];
            } else {
                this.panel = [true,true,true,true,true,true,true,true,true,true];
            }
        },
        getCurrentData() {
            this.getLocalStorage("panel");
        },
        getLocalStorage(name) {
            if (localStorage.getItem(name)){
                this[name] = JSON.parse(localStorage.getItem(name));
            }
        }
    },
    watch: {
        panel: {
            handler() {
                console.log("panel changed!");
                localStorage.setItem("panel", JSON.stringify(this.panel));
            },
            deep: true,
        },
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
    margin-left: 10px;
}
</style>