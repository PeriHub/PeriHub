<template>
    <div>
            <q-select 
                class="my-select"
                :options="cluster"
                v-model="job.cluster"
                label="Cluster"
                @change="changeToXml(); changeNumberOfTasks();"
                standout
                dense
            ></q-select>
            <q-input 
                class="my-input"
            v-model="job.tasks"
                  :disabled="job.cluster=='None'"
                :rules="[rules.required, rules.name]"
                label="Tasks"
                standout
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="job.time"
                v-show="job.cluster=='Cara'"
                :rules="[rules.required, rules.name]"
                label="Tasks"
                standout
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="job.account"
                v-show="job.cluster=='Cara'"
                :rules="[rules.required, rules.name]"
                label="Account"
                standout
                dense
            ></q-input>
        </div>
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