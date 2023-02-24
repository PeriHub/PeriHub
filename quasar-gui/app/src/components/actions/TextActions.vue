<template>
    <div class="row">
        <q-btn flat icon="fas fa-sync-alt" @click="viewInputFile(false)" :disabled="!store.status.created">
            <q-tooltip>
                Reload Inputfile
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-save" @click="writeInputFile" :disabled="!store.status.created">
            <q-tooltip>
                Save Inputfile
            </q-tooltip>
        </q-btn>

        <q-space></q-space>
        
        <q-btn flat icon="fas fa-sync-alt" @click="getLogFile" :disabled="!store.status.created">
            <q-tooltip>
                Reload LogFile
            </q-tooltip>
        </q-btn>
        
        <q-toggle
            class="my-toggle"
            icon="fas fa-eye"
            v-model="monitorToggle"
            @change="monitorLogFile"
            dense
        ></q-toggle>
    </div>
</template>

<script>
    import { computed, defineComponent } from 'vue'
    import { useDefaultStore } from 'stores/default-store';
    import { useModelStore } from 'stores/model-store';
    import { useViewStore } from 'stores/view-store';
    import { inject } from 'vue'
    import { api } from 'boot/axios'
    import { useQuasar } from 'quasar'
    import rules from "assets/rules.js";

export default defineComponent({
    name: "ViewActions",
        setup() {
            const $q = useQuasar()
            const store = useDefaultStore();
            const modelStore = useModelStore();
            const viewStore = useViewStore();
            const modelData = computed(() => modelStore.modelData)
            const bus = inject('bus')

            return {
                store,
                viewStore,
                modelData,
                rules,
                bus,
            }
        },
        created() {
            this.bus.on('getLogFile', () => {
                this.getLogFile()
            })
            this.bus.on('viewInputFile', (loadFile) => {
                this.viewInputFile(loadFile)
            })
            this.bus.on('getStatus', () => {
                this.getStatus()
            })
        },
    data() {
        return {
            monitorToggle: false,
        };
    },
    methods: {
        async viewInputFile(loadFile) {

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                own_mesh: this.modelData.model.ownMesh,
                file_type: this.modelData.solver.filetype
            }

            api.get('/viewInputFile', {params})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
                this.viewStore.textOutput = response.data.data;
                if (loadFile) {
                    this.loadYamlString(response.data.data);
                }
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error,
                    icon: 'report_problem'
                })
            })
        },
        writeInputFile() {
            let params = {
                model_name: this.modelData.model.modelNameSelected,
                input_string: this.viewStore.textOutput,
                file_type: this.modelData.solver.filetype,
            }

            api.put('/writeInputFile', {params})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error.response.data.detail,
                    icon: 'report_problem'
                })
            })
        },
        monitorLogFile() {
            if (this.monitorToggle) {
                this.getLogFile();
                this.logInterval = setInterval(() => {
                this.getLogFile();
                }, 30000);
            } else {
                clearInterval(this.logInterval);
            }
        },
        async getLogFile() {

            this.viewStore.textLoading = true;

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                cluster: this.modelData.job.cluster
            }
            api.get('/getLogFile', {params})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
                this.viewStore.textOutput = response.data.data;
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error.response.data.detail,
                    icon: 'report_problem'
                })
            })

            this.viewStore.textLoading = false;

            this.getStatus();
        },
        async getStatus() {
            console.log("getStatus");
            api.get('/getStatus', {
                model_name: this.modelData.model.modelNameSelected,
                own_model: this.modelData.model.ownModel,
                cluster: this.modelData.job.cluster})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
                this.store.status = response.data.data
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error.response.data.detail,
                    icon: 'report_problem'
                })
            })
            if (this.store.status.results) {
                console.log("clearInterval");
                clearInterval(this.statusInterval);
            }
        },
    },
    mounted(){
        this.getStatus();
    }
})
</script>