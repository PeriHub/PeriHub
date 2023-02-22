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
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn flat icon="fas fa-save" @click="saveData">
            <q-tooltip>
                Save as JSON
            </q-tooltip>
        </q-btn>

        <q-btn v-if="!modelData.modelownModel" flat icon="fas fa-undo" @click="bus.emit('resetData')">
            <q-tooltip>
                Reset Data
            </q-tooltip>
        </q-btn>

        <q-btn v-if="modelData.modelmodelNameSelected=='RVE' & !modelData.modelownModel" flat icon="fas fa-cogs" @click="generateMesh">
            <q-tooltip>
                Generate Mesh
            </q-tooltip>
        </q-btn>

        <q-btn flat icon="fas fa-cogs" @click="generateModel">
            <q-tooltip>
                Generate Model
            </q-tooltip>
        </q-btn>

        <q-btn v-if="modelData.modelownModel" flat icon="fas fa-upload" @click="uploadMesh">
            <q-tooltip>
                Upload Mesh and Nodesets
            </q-tooltip>
        </q-btn>
        
        <q-btn flat icon="fas fa-download" @click="saveModel" :disabled="!store.status.created">
            <q-tooltip>
                Download Modelfiles
            </q-tooltip>
        </q-btn>
        
        <q-btn v-if="modelData.modelownModel" flat icon="fas fa-backward" @click="switchModels">
            <q-tooltip>
                Use predefined Models
            </q-tooltip>
        </q-btn>

        <q-space></q-space>

        <!-- <q-btn flat icon="fas fa-sort" @click="openHidePanels">
            <q-tooltip>
                Collapse/Expand all panel
            </q-tooltip>
        </q-btn> -->

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
    import { useViewStore } from 'stores/view-store';
    import { inject } from 'vue'
    import { api } from 'boot/axios'
    import { useQuasar } from 'quasar'
    import rules from "assets/rules.js";

export default defineComponent({
    name: "ModelActions",
        setup() {
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
        uploadMesh() {
            this.$refs.multifileInput.click();
        },
        uploadProps(id) {
            this.$refs.propsInput.click();
            this.selectedMaterial = id;
        },
        uploadSo() {
            this.$refs.multiSoInput.click();
        },
        onFilePicked(event) {
            const files = event.target.files;
            const filetype = files[0].type;
            if (files.length <= 0) {
                return false;
            }

            const fr = new FileReader();

            if (filetype == "application/json") {
                this.loadJsonFile(fr, files);
            } else if (files[0].name.includes(".yaml")) {
                this.loadYamlModel(fr, files);
            } else if (filetype == "text/xml") {
                this.loadXmlModel(fr, files);
            } else if (filetype == ".peridigm") {
                this.loadPeridigmModel(fr, files);
            } else if (files[0].name.includes(".gcode")) {
                this.gcodeFile = files;
                this.dialogGcode = true;
            } else {
                this.loadFeModel(files);
            }
        },
        onPropsFilePicked(event) {
            const files = event.target.files;

            const fr = new FileReader();
            fr.onload = (e) => {
                const input_string = e.target.result;

                let filtered_string = input_string.match(/\*User([\D\S]*?)\*/gi);
                let propsArray = filtered_string[0].split(/[\n,]/gi);
                propsArray = propsArray.slice(0, propsArray.length - 1);

                if (propsArray[1].match(/\d+/) == propsArray.length - 2) {
                this.materials[0].properties = [];
                for (var i = 2; i < propsArray.length; i++) {
                    this.addProp(0);
                    this.materials[0].properties[i - 2].value = propsArray[i].trim();
                }
                } else {
                console.log("Length of Propsarray unexpected");
                }
            };
            fr.readAsText(files.item(0));

            // console.log(input_string)
            // let filtered_string = input_string.search(/\*User([\D\S]*?)\*/i);
        },
        onMultiFilePicked(event) {
            const files = event.target.files;
            const filetype = files[0].type;
            if (files.length <= 0) {
                return false;
            }

            this.modelLoading = true;
            this.uploadfiles(files);

            this.bus.emit('viewPointData');
            this.modelLoading = false;
            this.snackbar = true;
        },
        async uploadfiles(files) {
            const formData = new FormData();
            for (var i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }

            // let headersList = {
            //     "Cache-Control": "no-cache",
            //     "Content-Type": "multipart/form-data",
            //     Authorization: this.authToken,
            // };

            // let reqOptions = {
            //     url: this.url + "uploadfiles",
            //     params: { model_name: this.modelData.model.modelNameSelected },
            //     data: formData,
            //     method: "POST",
            //     headers: headersList,
            // };

            // this.message = "Files have been uploaded";
            // await axios.request(reqOptions).catch((error) => {
            //     console.log(response);
            //     this.message = error;
            //     return;
            // });

            api.post('/uploadfiles', formData, 
            {model_name: this.modelData.model.modelNameSelected})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: 'Loading failed',
                    icon: 'report_problem'
                })
            })
        },
        loadYamlModel(fr, files) {
            this.modelData.model.ownMesh = false;
            this.modelData.model.ownModel = true;
            this.modelData.model.translated = false;

            this.modelData.model.modelNameSelected = files[0].name.split(".")[0];

            fr.onload = (e) => {
                const yaml = e.target.result;
                this.loadYamlString(yaml);
            };
            fr.readAsText(files.item(0));
        },
        loadXmlModel(fr, files) {
            this.modelData.model.ownMesh = false;
            this.modelData.model.ownModel = true;
            this.modelData.model.translated = false;

            this.modelData.model.modelNameSelected = files[0].name.split(".")[0];

            fr.onload = (e) => {
                const xml = e.target.result;
                var yaml = this.translateXMLtoYAML(xml);
                this.loadYamlString(yaml);
            };
            fr.readAsText(files.item(0));
        },
        async loadFeModel(files) {
            this.modelData.model.ownMesh = true;
            this.modelData.model.ownModel = true;
            this.modelData.model.translated = true;

            this.modelLoading = true;
            this.textLoading = true;

            if (files.length <= 0) {
                return false;
            }

            if (await this.checkFeSize(files)) {
                this.modelData.model.modelNameSelected = files[0].name.split(".")[0];
                const filetype = files[0].name.split(".")[1];

                await this.translateModel(files, filetype, true);
            } else {
                this.modelLoading = false;
                this.textLoading = false;
            }
        },
        async loadGcodeModel() {
            this.dialogGcode = false;
            this.modelData.model.ownMesh = false;
            this.modelData.model.ownModel = true;
            // this.modelData.model.translated = true;

            this.modelLoading = true;
            // this.textLoading = true;

            if (this.gcodeFile.length <= 0) {
                return false;
            }

            this.modelData.model.modelNameSelected = this.gcodeFile[0].name.split(".")[0];
            const filetype = this.gcodeFile[0].name.split(".")[1];

            await this.translatGcode(this.gcodeFile, true);
        },
        saveData() {
            var fileURL = window.URL.createObjectURL(
                new Blob([JSON.stringify(this.modelData)], { type: "application/json" })
            );
            var fileLink = document.createElement("a");
            fileLink.href = fileURL;
            fileLink.setAttribute("download", this.modelData.model.modelNameSelected + ".json");
            document.body.appendChild(fileLink);
            fileLink.click();
        },
        saveModel() {

            api.get('/getModel', 
            {model_name: this.modelData.model.modelNameSelected})
            .then((response) => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement("a");
                fileLink.href = fileURL;
                fileLink.setAttribute("download", "file.zip");
                document.body.appendChild(fileLink);
                fileLink.click();
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: 'Loading failed',
                    icon: 'report_problem'
                })
            })
        },
        async generateModel () {

            if (this.modelData.model.ownModel == false) {
                this.viewStore.modelLoading = true;
            }
            this.viewStore.textLoading = true;

            api.post('/generateModel', this.modelData, 
            {model_name: this.modelData.model.modelNameSelected})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
                this.bus.emit("viewInputFile",false)
                if (this.modelData.model.ownModel == false) {
                    this.bus.emit('viewPointData');
                }
            })
            .catch((error) => {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error,
                    icon: 'report_problem'
                })
            })

            this.viewStore.modelLoading = false;
            this.viewStore.textLoading = false;
            this.bus.emit("getStatus")
        },
        showTutorial() {
            var color = "gray";
            if (this.$cookie.get("darkMode") == "true") {
                color = "gray";
            } else {
                color = "white";
            }
            console.log(this.$cookie.get("darkMode"));
            console.log(color);

            const driver = new Driver({
                animate: true, // Animate while changing highlighted element
                opacity: 0.5,
                stageBackground: color,
            });

            // Define the steps for introduction
            driver.defineSteps([
                {
                element: "#model-configuration",
                popover: {
                    className: "first-step-popover-class",
                    title: "Title on Popover",
                    description: "Body of the popover",
                    position: "right",
                },
                },
                {
                element: "#model-output",
                popover: {
                    title: "Title on Popover",
                    description: "Body of the popover",
                    position: "left",
                },
                },
                {
                element: "#button-runModel",
                popover: {
                    title: "Title on Popover",
                    description: "Body of the popover",
                    position: "bottom",
                },
                },
            ]);

            // Start the introduction
            driver.start();
        },
    },
})
</script>