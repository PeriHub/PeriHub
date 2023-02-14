<template>
    <div class="row">
        <q-btn flat icon="fas fa-upload" @click="readData">
            <q-tooltip>
                Load Model
            </q-tooltip>
        </q-btn>
        <input
            type="file"
            style="display: none"
            ref="fileInput"
            accept="application/json,application/xml,.yaml,.peridigm,.bdf,.cdb,.inp,.gcode"
            @change="onFilePicked"
        />
        <input
          type="file"
          style="display: none"
          ref="multifileInput"
          multiple
          accept="text/plain,.g"
          @change="onMultiFilePicked"
        />
        <input
          type="file"
          style="display: none"
          ref="propsInput"
          multiple
          accept=".inp"
          @change="onPropsFilePicked"
        />
        <input
          type="file"
          style="display: none"
          ref="multiSoInput"
          multiple
          accept=".so"
          @change="onMultiFilePicked"
        />
        <q-dialog v-model="dialogGcode" persistent max-width="800">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Gcode Translator</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Which variable do you want to display ?
                    <q-input
                        v-model="gcodeDiscretization"
                        :rules="[rules.float]"
                        label="Discretization"
                        clearable
                        outlined
                    ></q-input>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Ok" color="primary" v-close-popup @click="loadGcodeModel"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup @click="dialogGcode = false"></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn flat icon="fas fa-save" @click="saveData">
            <q-tooltip>
                Save as JSON
            </q-tooltip>
        </q-btn>

        <q-btn v-if="!model.ownModel" flat icon="fas fa-undo" @click="resetData">
            <q-tooltip>
                Reset Data
            </q-tooltip>
        </q-btn>

        <q-btn v-if="model.modelNameSelected=='RVE' & !model.ownModel" flat icon="fas fa-cogs" @click="generateMesh">
            <q-tooltip>
                Generate Mesh
            </q-tooltip>
        </q-btn>

        <q-btn flat icon="fas fa-cogs" @click="generateModel">
            <q-tooltip>
                Generate Model
            </q-tooltip>
        </q-btn>

        <q-btn v-if="model.ownModel" flat icon="fas fa-upload" @click="uploadMesh">
            <q-tooltip>
                Upload Mesh and Nodesets
            </q-tooltip>
        </q-btn>
        
        <q-btn flat icon="fas fa-download" @click="saveModel" :disabled="!status.created">
            <q-tooltip>
                Download Modelfiles
            </q-tooltip>
        </q-btn>
        
        <q-btn v-if="model.ownModel" flat icon="fas fa-backward" @click="switchModels">
            <q-tooltip>
                Use predefined Models
            </q-tooltip>
        </q-btn>

        <q-space></q-space>

        <q-btn flat icon="fas fa-sort" @click="openHidePanels">
            <q-tooltip>
                Collapse/Expand all panel
            </q-tooltip>
        </q-btn>

        <q-btn flat icon="fas fa-info" @click="showTutorial">
            <q-tooltip>
                Show Tutorial
            </q-tooltip>
        </q-btn>
    </div>
</template>

<script>
    import { computed, defineComponent } from 'vue'
    import { useDefaultStore } from 'stores/default-store';
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import { api } from 'boot/axios'
    import { useQuasar } from 'quasar'
    import rules from "assets/rules.js";

export default defineComponent({
    name: "ModelActions",
        setup() {
            const $q = useQuasar()
            const store = useDefaultStore();
            const status = computed(() => store.status)
            const modelStore = useModelStore();
            const model = computed(() => modelStore.model)
            const bus = inject('bus')

            function generateModel () {
                let modeldata = JSON.parse(
                    '{"model": ' +
                    JSON.stringify(modelStore.model) +
                    ",\n" +
                    '"materials": ' +
                    JSON.stringify(modelStore.materials) +
                    ",\n" +
                    '"damages": ' +
                    JSON.stringify(modelStore.damages) +
                    ",\n" +
                    '"blocks": ' +
                    JSON.stringify(modelStore.blocks) +
                    ",\n" +
                    '"contact": ' +
                    JSON.stringify(modelStore.contact) +
                    ",\n" +
                    '"boundaryConditions": ' +
                    JSON.stringify(modelStore.boundaryConditions) +
                    ",\n" +
                    '"bondFilters": ' +
                    JSON.stringify(modelStore.bondFilters) +
                    ",\n" +
                    '"computes": ' +
                    JSON.stringify(modelStore.computes) +
                    ",\n" +
                    '"outputs": ' +
                    JSON.stringify(modelStore.outputs) +
                    ",\n" +
                    '"solver": ' +
                    JSON.stringify(modelStore.solver) +
                    ",\n" +
                    '"job": ' +
                    JSON.stringify(modelStore.job) +
                    "}"
                )

                api.post('/generateModel', modeldata, {model_name: modelStore.model.modelNameSelected})
                .then((response) => {
                    console.log(response)
                    data.value = response.data
                })
                .catch(() => {
                    $q.notify({
                    color: 'negative',
                    position: 'top',
                    message: 'Loading failed',
                    icon: 'report_problem'
                    })
                })
            }

            return {
                status,
                model,
                rules,
                bus,
                generateModel
            }
        },
    data() {
        return {
            dialogGcode: false,
            gcodeDiscretization: 1,
        };
    },
    methods: {
        readData() {
            this.$refs.fileInput.click();
        },
        async loadGcodeModel() {
            this.dialogGcode = false;
            this.model.ownMesh = false;
            this.model.ownModel = true;
            // this.model.translated = true;

            this.modelLoading = true;
            // this.textLoading = true;

            if (this.gcodeFile.length <= 0) {
                return false;
            }

            this.model.modelNameSelected = this.gcodeFile[0].name.split(".")[0];
            const filetype = this.gcodeFile[0].name.split(".")[1];

            await this.translatGcode(this.gcodeFile, true);
        },
    },
})
</script>