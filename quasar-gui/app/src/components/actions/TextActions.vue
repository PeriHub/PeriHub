<template>
    <div class="row">
        <q-btn flat icon="fas fa-sync-alt" @click="viewInputFile(false)" :disable="!store.status.created">
            <q-tooltip>
                Reload Inputfile
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-save" @click="writeInputFile" :disable="!store.status.created || viewStore.textId!='input'">
            <q-tooltip>
                Save Inputfile
            </q-tooltip>
        </q-btn>

        <q-space></q-space>
        
        <q-btn flat icon="fas fa-sync-alt" @click="getLogFile" :disable="!store.status.created">
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
    import { useQuasar } from 'quasar'
    import rules from "assets/rules.js";

export default defineComponent({
    name: "TextActions",
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
            logInterval: null,
        };
    },
    methods: {
        async viewInputFile(loadFile) {

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                model_folder_name: this.modelData.model.modelFolderName,
                own_mesh: this.modelData.model.ownMesh,
                file_type: this.modelData.solver.filetype
            }

            this.$api.get('/viewInputFile', {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
                this.viewStore.textOutput = response.data.data;
                this.viewStore.textId = "input" 
                if (loadFile) {
                    this.loadYamlString(response.data.data);
                }
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'bottom-right',
                    message: error,
                    icon: 'report_problem'
                })
            })
        },
        writeInputFile() {
            let params = {
                model_name: this.modelData.model.modelNameSelected,
                model_folder_name: this.modelData.model.modelFolderName,
                input_string: this.viewStore.textOutput,
                file_type: this.modelData.solver.filetype,
            }

            this.$api.put('/writeInputFile', '', {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
            })
            .catch( (error)=> {
                this.$q.notify({
                    type: 'negative',
                    message: error.response.data.detail
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
                model_folder_name: this.modelData.model.modelFolderName,
                cluster: this.modelData.job.cluster
            }
            this.$api.get('/getLogFile', {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
                this.viewStore.logOutput = response.data.data;
                this.viewStore.textId = "log" 
            })
            .catch( (error)=> {
                this.$q.notify({
                    type: 'negative',
                    message: error.response.data.detail
                })
            })

            this.viewStore.textLoading = false;

            this.getStatus();
        },
        async getStatus() {
            console.log("getStatus");

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                model_folder_name: this.modelData.model.modelFolderName,
                own_model: this.modelData.model.ownModel,
                cluster: this.modelData.job.cluster
            }

            this.$api.get('/getStatus', {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
                this.store.status = response.data.data
            })
            .catch( (error)=> {
                this.$q.notify({
                    type: 'negative',
                    message: error.response.data.detail
                })
            })
        },
    },
    mounted(){
        this.getStatus();
    },
    beforeUnmount() {
        clearInterval(this.logInterval);
    },
})
</script>