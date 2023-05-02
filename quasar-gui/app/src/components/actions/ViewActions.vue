<template>
    <div class="row">
        <q-btn flat icon="fas fa-play" @click="runModel" :disabled="!store.status.created || store.status.submitted">
            <q-tooltip>
                Submit Model
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-times" @click="cancelJob" :disabled="!store.status.submitted">
            <q-tooltip>
                Cancel Job
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-download" @click="dialog = true" :loading="resultsLoading" :disabled="resultsLoading || !store.status.results">
            <q-tooltip>
                Download Results
            </q-tooltip>
        </q-btn>
        <q-dialog v-model="dialog" persistent max-width="800">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Download Results</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Do you want to retrieve all modelfiles, including the
                    inputfiles and logdata or only the exodus results?
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="All data" color="primary" v-close-popup @click="saveResults(true)"></q-btn>
                    <q-btn flat label="Only the results" color="primary" v-close-popup @click="saveResults(false)"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn flat icon="fas fa-eye" @click="showResultsDialog" :disabled="!store.status.results">
            <q-tooltip>
                Show Results
            </q-tooltip>
        </q-btn>
        <q-btn v-if="port!=null" flat icon="fas fa-times" @click="closeTrame" :disabled="!store.status.results">
            <q-tooltip>
                Close Trame
            </q-tooltip>
        </q-btn>
        <q-dialog v-model="dialogShowResults" persistent max-width="800">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Show Results</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Which output do you want to show ?
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-select"
                        :options="modelData.outputs"
                        option-label="name"
                        option-value="name"
                        emit-value
                        v-model="showResultsOutputName"
                        label="Output Name"
                        standout
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Show" color="primary" v-close-popup @click="showResults(showResultsOutputName)"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn v-if="viewStore.viewId=='trame'" flat icon="fas fa-external-link-alt" @click="openResults">
            <q-tooltip>
                Open Results
            </q-tooltip>
        </q-btn>
        <q-btn v-if="modelData.job.cluster=='Cara'" flat icon="fas fa-external-link-alt" @click="openCara">
            <q-tooltip>
                CARA Enginframe
            </q-tooltip>
        </q-btn>
        <q-btn v-if="['CompactTension', 'KICmodel', 'KIICmodel', 'ENFmodel'].includes(modelData.model.modelNameSelected)" flat icon="fas fa-image" @click="getFractureAnalysis()" :disabled="!store.status.results">
            <q-tooltip>
                Show Fracture Analysis
            </q-tooltip>
        </q-btn>
        <q-btn v-if="viewStore.viewId=='image'" flat icon="fas fa-download" @click="downloadModelImage()" :disabled="!store.status.results">
            <q-tooltip>
                Download Image
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-chart-line" @click="dialogGetPlot = true, updatePlotVariables()" :disabled="!store.status.results || modelData.computes.length==0">
            <q-tooltip>
                Show Plot
            </q-tooltip>
        </q-btn>
        <q-dialog v-model="dialogGetPlot" persistent max-width="800">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Show Plot</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Which variable do you want to use for the x-axis?
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-select"
                        :options="modelData.outputs"
                        option-label="name"
                        option-value="name"
                        emit-value
                        v-model="getPlotOutput"
                        label="Output Name"
                        standout
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-select"
                        :options="getPlotVariables"
                        v-model="getPlotVariableX"
                        label="Variable"
                        standout
                        dense
                    ></q-select>
                    <q-select 
                        class="my-select"
                        :options="getImageAxis"
                        :readonly="getPlotVariableX=='Damage'"
                        v-model="getPlotAxisX"
                        label="Axis"
                        standout
                        dense
                    ></q-select>
                    <q-toggle
                        class="my-toggle"
                        v-model="getPlotAbsoluteX"
                        label="Absolute"
                        dense
                    ></q-toggle>
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-select"
                        :options="getPlotVariables"
                        v-model="getPlotVariableY"
                        label="Variable"
                        standout
                        dense
                    ></q-select>
                    <q-select 
                        class="my-select"
                        :options="getImageAxis"
                        :readonly="getPlotVariableY=='Damage'"
                        v-model="getPlotAxisY"
                        label="Axis"
                        standout
                        dense
                    ></q-select>
                    <q-toggle
                        class="my-toggle"
                        v-model="getPlotAbsoluteY"
                        label="Absolute"
                        dense
                    ></q-toggle>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Show" color="primary" v-close-popup @click="getPlot(false)"></q-btn>
                    <q-btn flat label="Append" color="primary" v-close-popup @click="getPlot(true)"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn flat icon="fas fa-image" @click="dialogGetImagePython = true" :disabled="!store.status.results">
            <q-tooltip>
                Show Image
            </q-tooltip>
        </q-btn>
        <q-dialog v-model="dialogGetImagePython" persistent max-width="800">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Show Image</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Which variable do you want to display?
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-select"
                        :options="modelData.outputs"
                        option-label="name"
                        option-value="name"
                        emit-value
                        v-model="getImageOutput"
                        label="Output Name"
                        standout
                        dense
                    ></q-select>
                    <q-select 
                        class="my-select"
                        :options="getImageVariable"
                        v-model="getImageVariableSelected"
                        label="Variable"
                        standout
                        dense
                    ></q-select>
                    <q-select 
                        class="my-select"
                        :options="getImageAxis"
                        :readonly="getImageVariableSelected=='Damage'"
                        v-model="getImageAxisSelected"
                        label="Axis"
                        standout
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-input 
                        class="my-input"
                        v-model="getImageDisplFactor"
                        :rules="[rules.required, rules.name]"
                        label="Displacement Factor"
                        standout
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-show="!getImageTriangulate"
                        v-model="getImageMarkerSize"
                        :rules="[rules.required, rules.name]"
                        label="Marker Size"
                        standout
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-model="getImageStep"
                        :rules="[rules.required, rules.name]"
                        label="Time Step"
                        standout
                        dense
                    ></q-input>
                    <q-toggle
                        class="my-toggle"
                        v-model="getImageTriangulate"
                        label="Triangulate"
                        dense
                    ></q-toggle>
                    <q-input 
                        class="my-input"
                        v-model="getImageDxFactor"
                        :rules="[rules.required, rules.name]"
                        label="Dx Factor"
                        standout
                        dense
                    ></q-input>
                    <q-toggle
                        class="my-toggle"
                        v-model="getImageThreeD"
                        label="Three Dimensional"
                        dense
                    ></q-toggle>
                    <div class="row my-row" v-show="getImageThreeD">
                        <q-input 
                            class="my-input"
                            v-model="getImageElevation"
                            label="Elevation"
                            standout
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="getImageAzimuth"
                            label="Azimuth"
                            standout
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="getImageRoll"
                            label="Roll"
                            standout
                            dense
                        ></q-input>
                    </div>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Show" color="primary" v-close-popup @click="getImagePython"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <!-- <q-btn flat icon="fas fa-image" @click="getG1c" :disabled="!store.status.results">
            <q-tooltip>
                Show G1c
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-image" @click="getG2c" :disabled="!store.status.results">
            <q-tooltip>
                Get GIIC
            </q-tooltip>
        </q-btn> -->
        <!-- <q-btn flat icon="fas fa-chess-board" @click="bus.emit('viewPointData')" :disabled="!store.status.created">
            <q-tooltip>
                Show Model
            </q-tooltip>
        </q-btn> -->
        <q-btn flat icon="fas fa-trash" @click="dialogDeleteData = true">
            <q-tooltip>
                Delete Data
            </q-tooltip>
        </q-btn>
        <q-dialog v-model="dialogDeleteData" persistent max-width="500">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Delete Data</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Do you want to delete the selected Model data, all Cookies or
                  all User data?
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Model data" color="primary" v-close-popup @click="dialogDeleteModel = true"></q-btn>
                    <q-btn flat label="Cookies" color="primary" v-close-popup @click="dialogDeleteCookies = true"></q-btn>
                    <q-btn flat label="User data" color="primary" v-close-popup @click="dialogDeleteUserData = true"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>
        <q-dialog v-model="dialogDeleteModel" persistent max-width="500">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Delete Model</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Are you sure, you want to delete the Model?
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Yes" color="primary" v-close-popup @click="deleteModel"></q-btn>
                    <q-btn flat label="No" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>
        <q-dialog v-model="dialogDeleteCookies" persistent max-width="500">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Delete Cookies</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Are you sure, you want to delete all Cookies?
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Yes" color="primary" v-close-popup @click="deleteCookies"></q-btn>
                    <q-btn flat label="No" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>
        <q-dialog v-model="dialogDeleteUserData" persistent max-width="500">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Delete User Data</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                    Are you sure, you want to delete the User Data?
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Yes" color="primary" v-close-popup @click="deleteUserData"></q-btn>
                    <q-btn flat label="No" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>
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

    const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
    name: "ViewActions",
        setup() {
            const $q = useQuasar()
            const store = useDefaultStore();
            const viewStore = useViewStore();
            const modelStore = useModelStore();
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
            resultsLoading: false,
            dialog: false,
            dialogShowResults: false,
            dialogGetImage: false,
            showResultsOutputName: "Output1",

            dialogGetPlot: false,
            getPlotVariables: [],
            getPlotOutput: "Output1",
            getPlotVariableX: "Time",
            getPlotAxisX: "X",
            getPlotAbsoluteX: true,
            getPlotVariableY: "External_Displacement",
            getPlotAxisY: "X",
            getPlotAbsoluteY: true,

            dialogDeleteData: false,
            dialogDeleteModel: false,
            dialogDeleteCookies: false,
            dialogDeleteUserData: false,

            dialogGetImagePython: false,
            getImageOutput: "Output1",
            getImageVariable: [
                "Displacement",
                "Force",
                "Damage",
                "Temperature",
                "Partial_StressX",
                "Partial_StressY",
                "Partial_StressZ",
                "Number_Of_Neighbors",
            ],
            getImageVariableSelected: "Displacement",
            getImageAxis: ["Magnitude", "X", "Y", "Z"],
            getImageAxisSelected: "Magnitude",
            getImageDisplFactor: 20,
            getImageMarkerSize: 16,
            getImageTriangulate: false,
            getImageDxFactor: 1.5,
            getImageStep: -1,
            getImageThreeD: false,
            getImageElevation: 30,
            getImageAzimuth: 30,
            getImageRoll: 0,

            statusInterval: null,
            port: null,

            plotRawData: null,
        };
    },
    methods: {
        async runModel() {

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                file_type: this.modelData.solver.filetype,
            }

            this.$api.put('/runModel', this.modelData, {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
            })
            .catch((error) => {
                let message = "";
                if (error.response.status == 422) {
                    for (let i in error.response.data.detail) {
                        message += error.response.data.detail[i].loc[1] + " ";
                        message += error.response.data.detail[i].loc[2] + ", ";
                        message += error.response.data.detail[i].loc[3] + ", ";
                        message += error.response.data.detail[i].msg + "\n";
                    }
                    message = message.slice(0, -2);
                } else {
                    message = error.response.data.detail;
                }
                this.$q.notify({
                    color: 'negative',
                    position: 'bottom-right',
                    message: message,
                    icon: 'report_problem'
                })
            })

            this.bus.emit("getLogFile")
            // this.monitorStatus(true);
            this.monitorStatus(false);
        },
        async cancelJob() {

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                cluster: this.modelData.job.cluster
            }
            this.$api.put('/cancelJob', '', {params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'bottom-right',
                    message: 'Failed',
                    icon: 'report_problem'
                })
            })

            this.monitorStatus(false);
        },
        monitorStatus(setClear) {
            this.bus.emit("getStatus")
            if (setClear) {
                this.statusInterval = setInterval(() => {
                    this.bus.emit("getStatus")
                    if (this.store.status.results | !this.store.status.submitted) {
                        console.log("clearInterval");
                        clearInterval(this.statusInterval);
                    }
                    }, 30000);
            } else {
                clearInterval(this.statusInterval);
            }
        },
        async saveResults(allData) {
            this.resultsLoading = true;

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                cluster: this.modelData.job.cluster,
                allData: allData,
            }
            await this.$api.get('/getResults', {params, responseType: "blob"})
            .then((response) => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement("a");
                fileLink.href = fileURL;
                fileLink.setAttribute(
                    "download",
                    this.modelData.model.modelNameSelected + ".zip"
                );
                document.body.appendChild(fileLink);
                fileLink.click();
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'bottom-right',
                    message: 'Failed',
                    icon: 'report_problem'
                })
            })

            this.resultsLoading = false;
        },
        openCara() {
            window.open("https://cara.dlr.de/enginframe/vdi/vdi.xml", "_blank");
        },
        openResults() {
            window.open(this.viewStore.resultPort, "_blank");
        },
        showResultsDialog() {
            if(this.modelData.outputs.length==1){
                this.showResults(this.modelData.outputs[0].name)
            }else{
                this.dialogShowResults = true
            }
        },
        async showResults(outputName) {
            this.viewStore.modelLoading = true;

            var index = this.modelData.outputs.findIndex((o) => o.name == outputName);

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                output_name: this.modelData.outputs[index].name,
                output_list: this.modelData.outputs[index].selectedOutputs.toString(),
                dx_value: this.viewStore.dx_value,
                num_of_blocks: this.modelData.blocks.length,
                duration: 600
            }

            console.log(this.port)
            await this.$trameApi.post('/launchTrameInstance', '',{params})
            .then((response) => {
                this.$q.notify({
                    message: response.data.message
                })
                this.port = response.data.data
            })
            .catch( (error)=> {
                this.$q.notify({
                    type: 'negative',
                    message: error.response.data.detail
                })
                
                this.viewStore.modelLoading = false;
                return;
            })
            
            if (process.env.DEV) {
                this.viewStore.resultPort =
                process.env.TRAME_API.slice(0, process.env.TRAME_API.length - 4) + this.port;
            } else {
                let id = parseInt(this.port) - 6040;
                this.viewStore.resultPort =
                "http://perihub-trame-gui" +
                id.toString() +
                ".fa-services.intra.dlr.de:443";
            }
            // console.log(this.port)
            // console.log(process.env.TRAME_API)
            // console.log(this.viewStore.resultPort)

            await sleep(17000);
            this.viewStore.modelLoading = false;
            window.open(this.viewStore.resultPort, "_blank");

            // this.viewStore.viewId = "trame";
            // document.querySelectorAll("iframe").forEach(function (e) {
            //     e.src += "";
            // });
        },
        closeTrame() {
            let params = {
                port: this.port,
                cron: false,
            }

            this.$trameApi.post('/closeTrameInstance', '', {params})
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
            this.port = "";
        },
        updatePlotVariables() {
            let items = [];

            for (var i = 0; i < this.modelData.computes.length; i++) {
                items.push(this.modelData.computes[i].name);
            }
            items.push("Time");
            this.getPlotVariables = items;
        },
        async getPlot(append) {
            this.viewStore.modelLoading = true;

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                cluster: this.modelData.job.cluster,
                output: this.getPlotOutput,
                x_variable: this.getPlotVariableX,
                x_axis: this.getPlotAxisX,
                x_absolute: this.getPlotAbsoluteX,
                y_variable: this.getPlotVariableY,
                y_axis: this.getPlotAxisY,
                y_absolute: this.getPlotAbsoluteY,
            }
            await this.$api.get('/getPlot', {params})
            .then((response) => {
                this.plotRawData = response.data.data
                this.$q.notify({
                    message: response.data.message,
                })
            })
            .catch(() => {
                this.$q.notify({
                    type: 'negative',
                    message: 'Failed',
                })
            })

            let newPlot = {
                name: "",
                x: [],
                y: [],
                type: "scatter",
            };

            newPlot.x = this.plotRawData[0];
            newPlot.y = this.plotRawData[1];
            newPlot.name = this.getPlotVariableY;

            if (append) {
                this.viewStore.plotData.push(newPlot);
            } else {
                let newPlotData = [newPlot];
                this.viewStore.plotData = newPlotData;
            }

            this.viewStore.viewId = "plotly";
            this.viewStore.modelLoading = false;
        },
        async getImagePython() {

            this.viewStore.modelLoading = true;

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                cluster: this.modelData.job.cluster,
                output: this.getImageOutput,
                variable: this.getImageVariableSelected,
                axis: this.getImageAxisSelected,
                displ_factor: this.getImageDisplFactor,
                marker_size: this.getImageMarkerSize,
                length: this.modelData.model.length,
                height: this.modelData.model.height,
                triangulate: this.getImageTriangulate,
                dx_value: this.viewStore.dx_value * this.getImageDxFactor,
                step: this.getImageStep,
                three_d: this.getImageThreeD,
                elevation: this.getImageElevation,
                azimuth: this.getImageAzimuth,
                roll: this.getImageRoll,
            }

            await this.$api.get('/getImagePython', {params, responseType: "blob"})
            .then((response) => {
                this.viewStore.modelImg = window.URL.createObjectURL(new Blob([response.data]))
            })
            .catch((error) => {
                console.log(error.response)
                console.log(error.response.detail)
                this.$q.notify({
                    type: 'negative',
                    message: error.response.statusText
                })
            })

            this.viewStore.viewId = "image";
            this.viewStore.modelLoading = false;
        },
        async getFractureAnalysis() {

            this.viewStore.modelLoading = true;

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                length: this.modelData.model.length,
                height: this.modelData.model.height,
                crack_length: this.modelData.model.cracklength,
                young_modulus: this.modelData.materials[0].youngsModulus,
                poissions_ratio: this.modelData.materials[0].poissonsRatio,
                yield_stress: this.modelData.materials[0].yieldStress,
                cluster: this.modelData.job.cluster,
                output: "Output2"
            }

            await this.$api.get('/getFractureAnalysis', {params, responseType: "blob"})
            .then((response) => {
                this.viewStore.modelImg = window.URL.createObjectURL(new Blob([response.data]))
                this.$q.notify({
                    message: "Fracture analyzed",
                })
            })
            .catch((error) => {
                this.$q.notify({
                    type: 'negative',
                    message: JSON.stringify(error.message)
                })
            })

            this.viewStore.viewId = "image";
            this.viewStore.modelLoading = false;
        },
        async downloadModelImage() {
            var fileLink = document.createElement("a");
            fileLink.href = this.viewStore.modelImg;
            fileLink.setAttribute("download", this.modelData.model.modelNameSelected + ".png");
            document.body.appendChild(fileLink);
            fileLink.click();
        },
        async getG1c() {
            let headersList = {
                "Cache-Control": "no-cache",
                Authorization: this.authToken,
            };

            let reqOptions = {
                url: this.url + "calculateG1c",
                params: {
                youngs_modulus: this.materials[0].youngsModulus,
                model_name: this.model.modelNameSelected,
                cluster: this.job.cluster,
                },
                data: this.model,
                method: "POST",
                responseType: "blob",
                headers: headersList,
            };

            this.viewStore.modelLoading = true;
            await axios
                .request(reqOptions)
                .then(
                (response) =>
                    (this.modelImg = window.URL.createObjectURL(
                    new Blob([response.data])
                    ))
                )
                .catch((error) => {
                this.message = error;
                this.snackbar = true;
                this.viewStore.modelLoading = false;
                return;
                });
            this.viewStore.viewId = 0;
            this.viewStore.modelLoading = false;
        },
        async getG2c() {
            let headersList = {
                "Cache-Control": "no-cache",
                Authorization: this.authToken,
            };

            let reqOptions = {
                url: this.url + "calculateG2c",
                params: {
                model_name: this.model.modelNameSelected,
                cluster: this.job.cluster,
                output: this.getG1cOutput,
                },
                data: this.model,
                method: "POST",
                responseType: "application/json",
                headers: headersList,
            };

            this.viewStore.modelLoading = true;
            var giic = 0;
            await axios
                .request(reqOptions)
                .then((response) => (giic = response.data))
                .catch((error) => {
                this.message = error;
                this.snackbar = true;
                this.viewStore.modelLoading = false;
                return;
                });
            console.log(giic);
            this.message = "GIIC = " + giic;
            this.snackbar = true;

            this.viewStore.modelLoading = false;
        },
    },
    beforeUnmount() {
        clearInterval(this.statusInterval);
    },
})
</script>