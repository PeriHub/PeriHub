<template>
    <q-list bordered class="rounded-borders">
        <q-expansion-item
            expand-separator
            icon="fas fa-flask"
            label="Job"
            caption="John Doe"
        >
            <q-select 
                class="my-input"
                :options="cluster"
                v-model="job.cluster"
                label="Cluster"
                @change="changeToXml(); changeNumberOfTasks();"
                outlined
                dense
            ></q-select>
            <q-input 
                class="my-input"
            v-model="job.tasks"
                  :disabled="job.cluster=='None'"
                :rules="[rules.required, rules.name]"
                label="Tasks"
                outlined
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="job.time"
                v-show="job.cluster=='Cara'"
                :rules="[rules.required, rules.name]"
                label="Tasks"
                outlined
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="job.account"
                v-show="job.cluster=='Cara'"
                :rules="[rules.required, rules.name]"
                label="Account"
                outlined
                dense
            ></q-input>
        </q-expansion-item>
    </q-list>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
  
    export default defineComponent({
        name: 'JobSettings',
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
                cluster: ["Cara", "None"], //'FA-Cluster',
            };
        },
        methods: {
            changeToXml() {
                if (this.job.cluster == "FA-Cluster") {
                    this.solver.filetype = "xml";
                } else {
                    this.solver.filetype = "yaml";
                }
            },
            changeNumberOfTasks() {
                if (this.job.cluster == "FA-Cluster") {
                    if (this.job.tasks > 32) {
                    this.job.tasks = 32;
                    }
                } else if (this.job.cluster == "None") {
                    this.job.tasks = 1;
                }
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
    margin: 10px;
}
</style>