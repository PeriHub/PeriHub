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
        <q-btn v-if="port!=''" flat icon="fas fa-times" @click="closeTrame" :loading="resultsLoading" :disabled="!store.status.results">
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
                        class="my-input"
                        :options="outputs"
                        item-text="name"
                        v-model="showResultsOutputName"
                        label="Output Name"
                        outlined
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Show" color="primary" v-close-popup @click="showResults(showResultsOutputName)"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn v-if="viewId==3" flat icon="fas fa-external-link-alt" @click="openResults">
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
        <q-btn v-if="viewId==0" flat icon="fas fa-download" @click="downloadModelImage()" :disabled="!store.status.results">
            <q-tooltip>
                Download Image
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-chart-line" @click="dialogGetPlot = true" :disabled="!store.status.results">
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
                        class="my-input"
                        :options="outputs"
                        item-text="name"
                        v-model="getPlotOutput"
                        label="Output Name"
                        outlined
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-select 
                        class="my-input"
                        :options="getPlotVariables"
                        item-text="name"
                        v-model="getPlotVariableX"
                        label="Variable"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="getImageAxis"
                        :disabled="getPlotVariableX=='Damage'"
                        v-model="getPlotAxisX"
                        label="Axis"
                        outlined
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
                        class="my-input"
                        :options="getPlotVariables"
                        item-text="name"
                        v-model="getPlotVariableY"
                        label="Variable"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="getImageAxis"
                        :disabled="getPlotVariableY=='Damage'"
                        v-model="getPlotAxisY"
                        label="Axis"
                        outlined
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
                        class="my-input"
                        :options="outputs"
                        item-text="name"
                        v-model="getImageOutput"
                        label="Output Name"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="getImageVariable"
                        v-model="getImageVariableSelected"
                        label="Variable"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="getImageAxis"
                        :disabled="getImageVariableSelected=='Damage'"
                        v-model="getImageAxisSelected"
                        label="Axis"
                        outlined
                        dense
                    ></q-select>
                </q-card-section>
                <q-card-section class="q-pt-none">
                    <q-input 
                        class="my-input"
                        v-model="getImageDisplFactor"
                        :rules="[rules.required, rules.name]"
                        label="Displacement Factor"
                        outlined
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-model="getImageMarkerSize"
                        :rules="[rules.required, rules.name]"
                        label="Marker Size"
                        outlined
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-model="getImageStep"
                        :rules="[rules.required, rules.name]"
                        label="Time Step"
                        outlined
                        dense
                    ></q-input>
                    <q-toggle
                        class="my-toggle"
                        v-model="getImageTriangulate"
                        label="Triangulate"
                        dense
                    ></q-toggle>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Show" color="primary" v-close-popup @click="getImagePython"></q-btn>
                    <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-btn flat icon="fas fa-image" @click="getG1c" :disabled="!store.status.results">
            <q-tooltip>
                Show G1c
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-image" @click="getG2c" :disabled="!store.status.results">
            <q-tooltip>
                Get GIIC
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-chess-board" @click="bus.emit('viewPointData')" :disabled="!store.status.created">
            <q-tooltip>
                Show Model
            </q-tooltip>
        </q-btn>
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
    import { api } from 'boot/axios'
    import { useQuasar } from 'quasar'
    import rules from "assets/rules.js";

export default defineComponent({
    name: "ViewActions",
        setup() {
            const $q = useQuasar()
            const store = useDefaultStore();
            const viewStore = useViewStore();
            const viewId = computed(() => viewStore.viewId)
            const modelStore = useModelStore();
            const modelData = computed(() => modelStore.modelData)
            const bus = inject('bus')

            return {
                store,
                viewId,
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
            dialogGetPlot: false,
            dialogDeleteData: false,
            dialogDeleteModel: false,
            dialogDeleteCookies: false,
            dialogDeleteUserData: false,
            dialogGetImagePython: false,
            port: "",
        };
    },
    methods: {
        async runModel() {

            api.put('/runModel', this.modelData, 
            {model_name: this.modelData.model.modelNameSelected,FileType: this.solver.filetype})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
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
                    position: 'top',
                    message: message,
                    icon: 'report_problem'
                })
            })

            this.bus.emit("getLogFile")
            this.monitorStatus(true);
        },
        async cancelJob() {

            api.put('/cancelJob', 
            {model_name: this.modelData.model.modelNameSelected,Cluster: this.modelData.job.cluster,})
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
                    message: 'Failed',
                    icon: 'report_problem'
                })
            })

            this.monitorStatus(true);
        },
        async saveResults(allData) {
            this.resultsLoading = true;

            api.get('/getResults', 
            {model_name: this.modelData.model.modelNameSelected,Cluster: this.modelData.job.cluster, allData: allData})
            .then((response) => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement("a");
                fileLink.href = fileURL;
                fileLink.setAttribute(
                    "download",
                    this.model.modelNameSelected + ".zip"
                );
                document.body.appendChild(fileLink);
                fileLink.click();
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
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
            window.open(this.resultPort, "_blank");
        },
        showResultsDialog() {
            if(outputs.length==1){
                this.showResults(outputs[0].name)
            }else{
                dialogShowResults = true
            }
        },
        async showResults(outputName) {
            this.dialogShowResults = false;
            this.modelLoading = true;

            let headersList = {
                "Cache-Control": "no-cache",
                Authorization: this.authToken,
            };

            var index = this.outputs.findIndex((o) => o.name == outputName);

            let output_list = [];

            if (this.outputs[index].Displacement) {
                output_list.push("Displacement");
            }
            if (this.outputs[index].Force) {
                output_list.push("Force");
            }
            if (this.outputs[index].Velocity) {
                output_list.push("Velocity");
            }
            if (this.outputs[index].Damage) {
                output_list.push("Damage");
            }
            if (this.outputs[index].Partial_Stress) {
                output_list.push("Partial_StressX");
                output_list.push("Partial_StressY");
                output_list.push("Partial_StressZ");
            }
            if (this.outputs[index].Number_Of_Neighbors) {
                output_list.push("Number_Of_Neighbors");
            }
            if (this.outputs[index].Temperature) {
                output_list.push("Temperature");
            }

            api.post('/launchTrameInstance', {
                model_name: this.model.modelNameSelected,
                output_name: this.outputs[index].name,
                output_list: output_list.toString(),
                dx_value: this.dx_value,
                duration: 600})
            .then((response) => {
                this.$q.notify({
                    color: 'positive',
                    position: 'top',
                    message: response.data.message,
                    icon: 'info'
                })
                this.port = response.data
            })
            .catch( (error)=> {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: error.response.data.detail,
                    icon: 'report_problem'
                })
            })
            
            if (process.env.VUE_APP_DEV) {
                this.resultPort =
                this.trameUrl.slice(0, this.trameUrl.length - 5) + this.port;
            } else {
                let id = parseInt(this.port) - 6040;
                this.resultPort =
                "http://perihub-trame-gui" +
                id.toString() +
                ".fa-services.intra.dlr.de:443";
            }

            await sleep(17000);
            this.modelLoading = false;

            this.viewId = 3;
            document.querySelectorAll("iframe").forEach(function (e) {
                e.src += "";
            });
        },
        closeTrame() {
            let headersList = {
                "Cache-Control": "no-cache",
                Authorization: this.authToken,
            };

            let reqOptions = {
                url: this.trameUrl + "closeTrameInstance",
                params: {
                port: this.port,
                cron: false,
                },
                method: "POST",
                headers: headersList,
            };
            axios.request(reqOptions);
            console.log(reqOptions);
            this.port = "";
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

            this.modelLoading = true;
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
                this.modelLoading = false;
                return;
                });
            this.viewId = 0;
            this.modelLoading = false;
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

            this.modelLoading = true;
            var giic = 0;
            await axios
                .request(reqOptions)
                .then((response) => (giic = response.data))
                .catch((error) => {
                this.message = error;
                this.snackbar = true;
                this.modelLoading = false;
                return;
                });
            console.log(giic);
            this.message = "GIIC = " + giic;
            this.snackbar = true;

            this.modelLoading = false;
        },
    },
})
</script>