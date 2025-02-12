<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <q-btn flat icon="fas fa-play" @click="checkEnergy" :loading="submitLoading"
      :disable="submitLoading || !status.created" v-if="!status.submitted">
      <q-tooltip>
        Submit Model
      </q-tooltip>
    </q-btn>
    <q-dialog v-model="dialogEnergySavings" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Submit Model</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          Are you sure, you want to submit the Model?
          The current renewable energy share is {{ energyPercent }}%
        </q-card-section>
        <q-card-section class="q-pt-none">
          <RenewableView></RenewableView>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Yes" color="primary" v-close-popup @click="runModel"></q-btn>
          <!-- <q-btn flat label="Remind me later" color="primary" v-close-popup @click="runModel"></q-btn> -->
          <q-btn flat label="No" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn flat icon="fas fa-times" @click="cancelJob" :loading="submitLoading" v-if="status.submitted">
      <q-tooltip>
        Cancel Job
      </q-tooltip>
    </q-btn>
    <q-btn flat icon="fas fa-download" @click="dialog = true" :loading="resultsLoading"
      :disable="resultsLoading || !status.results">
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

    <q-btn flat icon="fas fa-eye" @click="viewStore.viewId = 'results'" :disable="!status.results">
      <q-tooltip>
        Show Results
      </q-tooltip>
    </q-btn>

    <q-btn v-if="['CompactTension', 'KICmodel', 'KIICmodel', 'ENFmodel'].includes(modelData.model.modelNameSelected)"
      flat icon="fas fa-image" @click="dialogGetFractureAnalysis = true" :disable="!status.results">
      <q-tooltip>
        Show Fracture Analysis
      </q-tooltip>
    </q-btn>
    <q-dialog v-model="dialogGetFractureAnalysis" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Show Fracture Analysis</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Which output do you want to analyse?
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getImageOutput" label="Output Name" standout dense></q-select>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.name]" label="Time Step"
            standout dense></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="getFractureAnalysis"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn v-if="['ENFmodel'].includes(modelData.model.modelNameSelected)" flat icon="fas fa-image"
      @click="dialogGetEnfAnalysis = true" :disable="!status.results">
      <q-tooltip>
        Show ENF Analysis
      </q-tooltip>
    </q-btn>
    <q-dialog v-model="dialogGetEnfAnalysis" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Show ENF Analysis</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Which output do you want to analyse?
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getImageOutput" label="Output Name" standout dense></q-select>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.name]" label="Time Step"
            standout dense></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="getEnfAnalysis"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn v-if="viewStore.viewId == 'image'" flat icon="fas fa-download" @click="downloadModelImage()"
      :disable="!status.results">
      <q-tooltip>
        Download Image
      </q-tooltip>
    </q-btn>
    <q-btn flat icon="fas fa-chart-line" @click="dialogGetPlot = true, updatePlotVariables()"
      :disable="!status.results || modelData.computes.length == 0">
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
          Which output do you want to plot?
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getPlotOutput" label="Output Name" standout dense></q-select>
        </q-card-section>
        <!-- <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="getPlotVariables" v-model="getPlotVariableX" label="Variable" standout
            dense></q-select>
          <q-select class="my-select" :options="getImageAxis" :readonly="getPlotVariableX == 'Damage'"
            v-model="getPlotAxisX" label="Axis" standout dense></q-select>
          <q-toggle class="my-toggle" v-model="getPlotAbsoluteX" label="Absolute" dense></q-toggle>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="getPlotVariables" v-model="getPlotVariableY" label="Variable" standout
            dense></q-select>
          <q-select class="my-select" :options="getImageAxis" :readonly="getPlotVariableY == 'Damage'"
            v-model="getPlotAxisY" label="Axis" standout dense></q-select>
          <q-toggle class="my-toggle" v-model="getPlotAbsoluteY" label="Absolute" dense></q-toggle>
        </q-card-section> -->
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="_getPlot(false)"></q-btn>
          <!-- <q-btn flat label="Append" color="primary" v-close-popup @click="_getPlot(true)"></q-btn> -->
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- <q-btn flat icon="fas fa-image" @click="dialogGetImagePython = true" :disable="!status.results">
      <q-tooltip>
        Show Image
      </q-tooltip>
    </q-btn> -->
    <!-- <q-dialog v-model="dialogGetImagePython" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Show Image</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Which variable do you want to display?
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getImageOutput" label="Output Name" standout dense></q-select>
          <q-select class="my-select" :options="getImageVariable" v-model="getImageVariableSelected" label="Variable"
            standout dense></q-select>
          <q-select class="my-select" :options="getImageAxis" :readonly="getImageVariableSelected == 'Damage'"
            v-model="getImageAxisSelected" label="Axis" standout dense></q-select>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input class="my-input" v-model="getImageDisplFactor" :rules="[rules.required, rules.name]"
            label="Displacement Factor" standout dense></q-input>
          <q-input class="my-input" v-show="!getImageTriangulate" v-model="getImageMarkerSize"
            :rules="[rules.required, rules.name]" label="Marker Size" standout dense></q-input>
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.name]" label="Time Step"
            standout dense></q-input>
          <q-toggle class="my-toggle" v-model="getImageTriangulate" label="Triangulate" dense></q-toggle>
          <q-input class="my-input" v-model="getImageDxFactor" :rules="[rules.required, rules.name]" label="Dx Factor"
            standout dense></q-input>
          <q-toggle class="my-toggle" v-model="getImageThreeD" label="Three Dimensional" dense></q-toggle>
          <div class="row my-row" v-show="getImageThreeD">
            <q-input class="my-input" v-model="getImageElevation" label="Elevation" standout dense></q-input>
            <q-input class="my-input" v-model="getImageAzimuth" label="Azimuth" standout dense></q-input>
            <q-input class="my-input" v-model="getImageRoll" label="Roll" standout dense></q-input>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="getImagePython"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog> -->

    <!-- <q-btn flat icon="fas fa-image" @click="getG1c" :disable="!status.results">
            <q-tooltip>
                Show G1c
            </q-tooltip>
        </q-btn>
        <q-btn flat icon="fas fa-image" @click="getG2c" :disable="!status.results">
            <q-tooltip>
                Get GIIC
            </q-tooltip>
        </q-btn> -->
    <!-- <q-btn flat icon="fas fa-chess-board" @click="bus.emit('viewPointData')" :disable="!status.created">
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
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { inject } from 'vue'
import { useQuasar } from 'quasar'
import axios, { AxiosInstance } from 'axios';
import { getCurrentEnergy, runModel, cancelJob, getResults, getPlot, getFractureAnalysis, deleteModel, deleteModelFromCluster, deleteUserData, deleteUserDataFromCluster } from 'src/client';
import rules from 'assets/rules.js';
import RenewableView from 'components/views/RenewableView.vue'

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
  name: 'ViewActions',
  components: {
    RenewableView
  },
  setup() {
    const $q = useQuasar()
    const store = useDefaultStore();
    const status = computed(() => store.status)
    const saveEnergy = computed(() => store.saveEnergy)
    const viewStore = useViewStore();
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)
    const bus = inject('bus')

    return {
      status,
      saveEnergy,
      viewStore,
      modelStore,
      modelData,
      rules,
      bus,
    }
  },
  data() {
    return {
      resultsLoading: false,
      submitLoading: false,
      dialogEnergySavings: false,
      energyPercent: 0,
      dialog: false,
      dialogShowResults: false,
      dialogGetImage: false,
      showResultsOutputName: 'Output1',

      dialogGetFractureAnalysis: false,
      dialogGetEnfAnalysis: false,

      dialogGetPlot: false,
      getPlotVariables: [],
      getPlotOutput: 'Output1',
      getPlotVariableX: 'Time',
      getPlotAxisX: 'X',
      getPlotAbsoluteX: true,
      getPlotVariableY: 'External_Displacement',
      getPlotAxisY: 'X',
      getPlotAbsoluteY: true,

      dialogDeleteData: false,
      dialogDeleteModel: false,
      dialogDeleteCookies: false,
      dialogDeleteUserData: false,

      //dialogGetImagePython: false,
      getImageOutput: 'Output1',
      getImageVariable: [
        'Displacement',
        'Force',
        'Damage',
        'Temperature',
        'Partial_StressX',
        'Partial_StressY',
        'Partial_StressZ',
        'Number_Of_Neighbors',
      ],
      getImageVariableSelected: 'Displacement',
      getImageAxis: ['Magnitude', 'X', 'Y', 'Z'],
      getImageAxisSelected: 'Magnitude',
      getImageDisplFactor: 20,
      getImageMarkerSize: 16,
      getImageTriangulate: false,
      getImageDxFactor: 1.5,
      getImageStep: -1,
      getImageThreeD: false,
      getImageElevation: 30,
      getImageAzimuth: 30,
      getImageRoll: 0,

      port: null,

      plotRawData: null,

      color: [
        '#00658b',
        '#d2ae3d',
        '#82a043',
        '#666666',
        '#3b98cb',
        '#f2cd51',
        '#a6bf51',
        '#858585',
        '#6cb9dc',
        '#f8de53',
        '#cad55c',
        '#b1b1b1',
        '#a7d3ec',
        '#fcea7a',
        '#d9df78',
        '#cfcfcf',
        '#d1e8fa',
        '#fff8be',
        '#e6eaaf',
        '#ebebeb'
      ]
    };
  },
  methods: {
    async checkEnergy() {
      if (this.saveEnergy) {
        await getCurrentEnergy()
          .then((response) => {
            this.$q.notify({
              message: response.message
            })
            this.energyPercent = response.da.data;
          })
          .catch((error) => {
            this.$q.notify({
              color: 'negative',
              position: 'bottom-right',
              message: response.message,
              icon: 'report_problem'
            })
          })
        console.log(this.energyPercent)
        // if (this.energyPercent < 75) {
        //   this.dialogEnergySavings = true
        // }else {
        //   this.runModel();
        // }
        this.dialogEnergySavings = true
      } else {
        this.runModel();
      }
    },
    async runModel() {

      this.submitLoading = true;
      this.viewStore.textLoading = true;

      await runModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, requestBody: this.modelData })
        .then((response) => {
          if (response.data) {
            this.$q.notify({
              message: response.message
            })
          }
          else {
            this.$q.notify({
              type: 'negative',
              message: response.message
            })
          }
        })
        .catch((error) => {
          let message = '';
          if (error.response != undefined) {
            if (error.response.status == 422) {
              for (let i in error.response.detail) {
                message += error.response.detail[i].loc[1] + ' ';
                message += error.response.detail[i].loc[2] + ', ';
                message += error.response.detail[i].loc[3] + ', ';
                message += error.response.detail[i].msg + '\n';
              }
              message = message.slice(0, -2);
            } else {
              message = error.response.detail;
            }
          } else {
            message = 'Internal Error';
          }
          this.$q.notify({
            color: 'negative',
            position: 'bottom-right',
            message: message,
            icon: 'report_problem'
          })
          this.submitLoading = false;
          throw new Error(message);
        })

      this.viewStore.textId = 'log';
      this.viewStore.viewId = 'jobs';
      await sleep(1000);
      this.bus.emit('getStatus');
      this.submitLoading = false;
      await sleep(10000);
      this.bus.emit('enableWebsocket');
    },
    async cancelJob() {

      this.submitLoading = true;
      await cancelJob({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster
      })
        .then((response) => {
          this.$q.notify({
            message: response.message
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

      this.bus.emit('getStatus');
      this.submitLoading = false;
    },
    async saveResults(allData) {
      this.resultsLoading = true;
      await getResults({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        output: this.getPlotOutput,
        tasks: this.modelData.job.tasks,
        cluster: this.modelData.job.cluster,
        allData: allData
      })
        .then((response) => {
          var fileURL = window.URL.createObjectURL(new Blob([response]));
          var fileLink = document.createElement('a');
          fileLink.href = fileURL;
          fileLink.setAttribute('download', this.modelData.model.modelNameSelected + '_' + this.modelData.model.modelFolderName + '.zip');
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
    updatePlotVariables() {
      let items = [];

      for (var i = 0; i < this.modelData.computes.length; i++) {
        items.push(this.modelData.computes[i].name);
      }
      items.push('Time');
      this.getPlotVariables = items;
    },
    async _getPlot(append) {
      this.viewStore.modelLoading = true;
      let plotRawData = null;

      await getPlot({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        output: this.getPlotOutput,
        tasks: this.modelData.job.tasks
      })
        .then((response) => {
          if (response.data == false) {
            this.$q.notify({
              type: 'negative',
              message: response.message,
            })
          } else {
            plotRawData = response.data
            this.$q.notify({
              message: response.message,
            })

            let tempData = []
            let tempLayout = structuredClone(this.viewStore.plotLayout)
            const firstPropety = Object.keys(plotRawData)[0]
            let id = 0
            for (const propertyName in plotRawData) {
              if (propertyName != firstPropety) {
                tempData.push({ name: propertyName, x: plotRawData[firstPropety], y: plotRawData[propertyName], type: 'scatter', marker: { color: this.color[id] } })
                id += 1
              }
            }
            tempLayout.xaxis.title = firstPropety
            tempLayout.title = this.$route.params.id

            this.viewStore.plotData = structuredClone(tempData)
            this.viewStore.plotLayout = structuredClone(tempLayout)

            this.viewStore.viewId = 'plotly';
          }
        })
        .catch(() => {
          this.$q.notify({
            type: 'negative',
            message: 'Failed',
          })
        })
      this.viewStore.modelLoading = false;
    },
    // async getImagePython() {

    //   this.viewStore.modelLoading = true;

    //   await getImagePython({
    //     model_name: this.modelData.model.modelNameSelected,
    //     model_folder_name: this.modelData.model.modelFolderName,
    //     cluster: this.modelData.job.cluster,
    //     tasks: this.modelData.job.tasks,
    //     output: this.getImageOutput,
    //     variable: this.getImageVariableSelected,
    //     axis: this.getImageAxisSelected,
    //     displ_factor: this.getImageDisplFactor,
    //     marker_size: this.getImageMarkerSize,
    //     length: this.modelData.model.length,
    //     height: this.modelData.model.height,
    //     triangulate: this.getImageTriangulate,
    //     dx_value: this.viewStore.dx_value * this.getImageDxFactor,
    //     step: this.getImageStep,
    //     three_d: this.getImageThreeD,
    //     elevation: this.getImageElevation,
    //     azimuth: this.getImageAzimuth,
    //     roll: this.getImageRoll
    //   })
    //     .then((response) => {
    //       this.viewStore.modelImg = window.URL.createObjectURL(new Blob([response]))
    //     })
    //     .catch((error) => {
    //       console.log(error.response)
    //       console.log(error.response.detail)
    //       this.$q.notify({
    //         type: 'negative',
    //         message: error.response.statusText
    //       })
    //       this.viewStore.modelLoading = false;
    //     })

    //   this.viewStore.viewId = 'image';
    //   this.viewStore.modelLoading = false;
    // },
    async getFractureAnalysis() {

      this.viewStore.modelLoading = true;

      const api = axios.create({ baseURL: 'http://localhost:8000', headers: { 'userName': 'dev', } });

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        length: this.modelData.model.length,
        height: this.modelData.model.height,
        crack_length: this.modelData.model.cracklength,
        young_modulus: this.modelData.materials[0].youngsModulus,
        poissions_ratio: this.modelData.materials[0].poissonsRatio,
        yield_stress: this.modelData.materials[0].yieldStress,
        cluster: this.modelData.job.cluster,
        tasks: this.modelData.job.tasks,
        output: this.getImageOutput,
        step: this.getImageStep,
      }

      await api.get('/results/getFractureAnalysis', { params, responseType: 'blob' })
        .then((response) => {
          console.log(response)
          this.viewStore.modelImg = window.URL.createObjectURL(new Blob([response.data]))
          this.$q.notify({
            message: 'Fracture analyzed',
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: JSON.stringify(error.message)
          })
          this.viewStore.modelLoading = false;
        })

      //https://github.com/hey-api/openapi-ts/issues/804
      // await getFractureAnalysis({
      //   modelName: this.modelStore.selectedModel.file,
      //   modelFolderName: this.modelData.model.modelFolderName,
      //   length: this.modelData.model.length,
      //   height: this.modelData.model.height,
      //   crackLength: this.modelData.model.cracklength,
      //   youngModulus: this.modelData.materials[0].youngsModulus,
      //   poissionsRatio: this.modelData.materials[0].poissonsRatio,
      //   yieldStress: this.modelData.materials[0].yieldStress,
      //   cluster: this.modelData.job.cluster,
      //   tasks: this.modelData.job.tasks,
      //   output: this.getImageOutput,
      //   step: this.getImageStep,
      // })
      //   .then((response) => {
      //     console.log(response)
      //     this.viewStore.modelImg = window.URL.createObjectURL(new Blob([response]))
      //     this.$q.notify({
      //       message: 'Fracture analyzed',
      //     })
      //   })
      //   .catch((error) => {
      //     this.$q.notify({
      //       type: 'negative',
      //       message: JSON.stringify(error.message)
      //     })
      //     this.viewStore.modelLoading = false;
      //   })

      this.viewStore.viewId = 'image';
      this.viewStore.modelLoading = false;
    },
    async downloadModelImage() {
      var fileLink = document.createElement('a');
      fileLink.href = this.viewStore.modelImg;
      fileLink.setAttribute('download', this.modelData.model.modelNameSelected + '.png');
      document.body.appendChild(fileLink);
      fileLink.click();
    },
    // async getG1c() {
    //   let headersList = {
    //     'Cache-Control': 'no-cache',
    //     Authorization: this.authToken,
    //   };

    //   let reqOptions = {
    //     url: this.url + 'calculateG1c',
    //     params: {
    //       youngs_modulus: this.materials[0].youngsModulus,
    //       model_name: this.model.modelNameSelected,
    //       model_folder_name: this.modelData.model.modelFolderName,
    //       cluster: this.job.cluster,
    //     },
    //     data: this.model,
    //     method: 'POST',
    //     responseType: 'blob',
    //     headers: headersList,
    //   };

    //   this.viewStore.modelLoading = true;
    //   await axios
    //     .request(reqOptions)
    //     .then(
    //       (response) =>
    //       (this.modelImg = window.URL.createObjectURL(
    //         new Blob([response.data])
    //       ))
    //     )
    //     .catch((error) => {
    //       this.message = error;
    //       this.snackbar = true;
    //       this.viewStore.modelLoading = false;
    //       return;
    //     });
    //   this.viewStore.viewId = 0;
    //   this.viewStore.modelLoading = false;
    // },
    async getEnfAnalysis() {
      this.viewStore.modelLoading = true;

      await getEnfAnalysis({
        modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName,
        length: this.modelData.model.length,
        width: this.modelData.model.width,
        crack_length: this.modelData.model.cracklength,
        cluster: this.modelData.job.cluster,
        tasks: this.modelData.job.tasks,
        output: this.getImageOutput,
        step: this.getImageStep,
      })
        .then((response) => {
          console.log(response)
          this.$q.notify({
            message: 'ENF analyzed',
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: JSON.stringify(error.message)
          })
          this.viewStore.modelLoading = false;
        })

      this.viewStore.modelLoading = false;
    },
    async deleteModel() {

      await deleteModel({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName
      })
        .then((response) => {
          this.$q.notify({
            message: response.message
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

      await deleteModelFromCluster({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster
      })
        .then((response) => {
          this.$q.notify({
            message: response.message
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
    },
    async deleteUserData() {

      await deleteUserData({ checkDate: false })
        .then((response) => {
          this.$q.notify({
            message: response.message
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

      await deleteUserDataFromCluster({
        cluster: this.modelData.job.cluster, checkDate: false
      })
        .then((response) => {
          this.$q.notify({
            message: response.message
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

      this.bus.emit('getStatus');
    },
    deleteCookies() {
      localStorage.removeItem('darkMode');
      localStorage.removeItem('modelData');
      localStorage.removeItem('panel');
    },
  },
})
</script>
