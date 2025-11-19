<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <q-btn flat icon="fas fa-play" @click="checkEnergy" :loading="submitLoading"
      :disable="submitLoading || !store.status.created || !store.status.meshfileExist" v-if="!store.status.submitted">
      <q-tooltip>
        <div v-if="!store.status.created"> Model not created yet</div>
        <div v-if="!store.status.meshfileExist"> Meshfile not created or uploaded yet</div>
        <div v-if="store.status.submitted">Model is submitted</div>
        <div v-if="!submitLoading && store.status.created && store.status.meshfileExist">Submit Model</div>
      </q-tooltip>
    </q-btn>

    <q-dialog v-model="dialogSubmitMultiple" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Submit Mulitple Models</div>
        </q-card-section>
        <q-card-section>
          <q-select filled v-model="jobIds" :options="jobIdsOptions" label="Multi with toggle" multiple map-options>
            <template v-slot:option="{ itemProps, opt, selected, toggleOption }">
              <q-item v-bind="itemProps">
                <q-item-section>
                  <!-- eslint-disable-next-line -->
                  <q-item-label v-html="opt" />
                </q-item-section>
                <q-item-section side>
                  <q-toggle :model-value="selected" @update:model-value="toggleOption(opt)" />
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Yes" color="primary" v-close-popup @click="runModel(jobIds!.join(','))"></q-btn>
          <!-- <q-btn flat label="Remind me later" color="primary" v-close-popup @click="runModel"></q-btn> -->
          <q-btn flat label="No" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

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
          <q-btn flat label="Yes" color="primary" v-close-popup @click="runModel()"></q-btn>
          <!-- <q-btn flat label="Remind me later" color="primary" v-close-popup @click="runModel"></q-btn> -->
          <q-btn flat label="No" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn flat icon="fas fa-times" @click="cancelJob" :loading="submitLoading" v-if="store.status.submitted">
      <q-tooltip>
        Cancel Job
      </q-tooltip>
    </q-btn>
    <q-btn flat icon="fas fa-download" @click="dialog = true" :loading="resultsLoading"
      :disable="resultsLoading || !store.status.results">
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
          inputfiles and logdata or only the exodus result?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="All data" color="primary" v-close-popup @click="saveResults(true)"></q-btn>
          <q-btn flat label="Only the result" color="primary" v-close-popup @click="saveResults(false)"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn flat icon="fas fa-eye" @click="viewStore.viewId = 'results'" :disable="!store.status.results">
      <q-tooltip>
        Show Results
      </q-tooltip>
    </q-btn>

    <q-btn v-if="['CompactTension', 'DCBmodel', 'KIICmodel', 'ENFmodel'].includes(modelStore.selectedModel.file)" flat
      icon="fas fa-image" @click="dialogGetFractureAnalysis = true" :disable="!store.status.results">
      <q-tooltip>
        Show Fracture Analysis
      </q-tooltip>
    </q-btn>
    <q-btn v-if="['CompactTension', 'DCBmodel', 'KIICmodel', 'ENFmodel'].includes(modelStore.selectedModel.file)" flat
      icon="fas fa-image" @click="dialogGetEnergyReleasePlot = true, updatePlotVariables()"
      :disable="!store.status.results">
      <q-tooltip>
        Show Energy Release Plot
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
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.int]" label="Time Step"
            standout dense></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="getFractureAnalysis"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogGetEnergyReleasePlot" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Show Energy Release Plot</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Which output do you want to analyse?
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.int]" label="Time Step"
            standout dense></q-input>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getPlotOutput" label="Exodus Output File" standout dense></q-select>
          <q-select class="my-select" :options="modelData.outputs" option-label="name" option-value="name" emit-value
            v-model="getPlotOutputCsv" label="CSV Output File" standout dense></q-select>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="getPlotVariables" v-model="getEnergyPlotVariableX"
            label="Displacement Variable" standout dense></q-select>
          <q-select class="my-select" :options="getPlotVariables" v-model="getEnergyPlotVariableY"
            label="Force Variable" standout dense></q-select>
          <q-select class="my-select" :options="getImageAxis" v-model="getImageAxisSelected" label="Axis" standout
            dense></q-select>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="getEnergyReleasePlot()"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn v-if="['DIN6034'].includes(modelStore.selectedModel.file)" flat icon="fas fa-image"
      @click="openGetEnfAnalysisDialog()" :disable="!store.status.results">
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
          <q-input class="my-input" v-model="getImageStep" :rules="[rules.required, rules.int]" label="Time Step"
            standout dense></q-input>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="computeKeys" emit-value v-model="getAnalysisVariables[0]"
            label="Load Variable" standout dense></q-select>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select class="my-select" :options="computeKeys" emit-value v-model="getAnalysisVariables[1]"
            label="Displacement Variable" standout dense></q-select>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Show" color="primary" v-close-popup @click="_getEnfAnalysis"></q-btn>
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
      :disable="!status.results || computes.length == 0 || !csvDefined()">
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
          <q-btn flat label="Show" color="primary" v-close-popup @click="_getPlot()"></q-btn>
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

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { exportFile } from 'quasar'
import { api } from 'boot/axios';
import { getCurrentEnergy, runModel, cancelJob, getEnfAnalysis, getPlot, deleteModel, deleteModelFromCluster, deleteUserData, deleteUserDataFromCluster } from 'src/client';
import type { Block, BondFilters, Compute, Damage, Material, Deviations } from 'src/client';
import rules from 'assets/rules.js';
import RenewableView from 'components/views/RenewableView.vue'

const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
  name: 'ViewActions',
  components: {
    RenewableView
  },
  setup() {
    const store = useDefaultStore();
    const status = computed(() => store.status)
    const saveEnergy = computed(() => store.saveEnergy)
    const viewStore = useViewStore();
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)
    const blocks = computed(() => modelStore.modelData.blocks) as unknown as Block[]
    const bondFilters = computed(() => modelStore.modelData.bondFilters) as unknown as BondFilters[]
    const computes = computed(() => modelStore.modelData.computes) as unknown as Compute[]
    const damages = computed(() => modelStore.modelData.damages) as unknown as Damage[]
    const materials = computed(() => modelStore.modelData.materials) as unknown as Material[]
    const deviations = computed(() => modelStore.modelData.deviations) as unknown as Deviations

    return {
      store,
      status,
      saveEnergy,
      viewStore,
      modelStore,
      modelData,
      blocks,
      bondFilters,
      computes,
      damages,
      materials,
      deviations,
      rules
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

      dialogSubmitMultiple: false,
      jobIdsOptions: [1, 2, 3],
      jobIds: [],

      dialogGetFractureAnalysis: false,
      dialogGetEnergyReleasePlot: false,
      dialogGetEnfAnalysis: false,

      dialogGetPlot: false,
      getPlotVariables: [] as string[],
      getPlotOutput: 'Output1',
      getPlotOutputCsv: 'Output2',
      getPlotVariableX: 'Time',
      getEnergyPlotVariableX: 'External_Displacement',
      getPlotAxisX: 'X',
      getPlotAbsoluteX: true,
      getPlotVariableY: 'External_Displacement',
      getEnergyPlotVariableY: 'External_Force',
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

      computeKeys: [] as string[],
      getAnalysisVariables: ['External_Forces', 'External_Displacements'],

      port: null,

      timer: null as NodeJS.Timeout | null,
      intervalCount: 0,

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
              message: "Energy saved"
            })
            this.energyPercent = response;
          })
          .catch(() => {
            this.$q.notify({
              color: 'negative',
              position: 'bottom-right',
              message: 'Failed',
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
      } else if (this.deviations.enabled) {
        const n = this.deviations.sampleSize;
        this.jobIdsOptions = Array.from({ length: n }, (_, i) => i + 1);
        this.dialogSubmitMultiple = true
      } else {
        await this.runModel();
      }
    },
    async runModel(jobIds: string | null = null) {
      this.submitLoading = true;
      this.viewStore.textLoading = true;

      await runModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, verbose: this.modelData.job.verbose, jobIds: jobIds, requestBody: this.modelData })
        .then(() => {
          this.$q.notify({
            message: 'Job submitted'
          })
          this.viewStore.textId = 'log';
          this.viewStore.viewId = 'jobs';
          this.intervalCount = 0;
          // eslint-disable-next-line
          this.timer = setInterval(this.checkStatus, 5000)
        })
        .catch((error) => {
          let message = '';
          if (error.response != undefined) {
            if (error.response.status == 422) {
              for (const i in error.response.detail) {
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
            message = error.body.detail;
          }
          this.$q.notify({
            color: 'negative',
            position: 'bottom-right',
            message: message,
            icon: 'report_problem'
          })
          this.submitLoading = false;
          this.viewStore.textLoading = false;
          // throw new Error(message);
        })

    },
    async checkStatus() {
      this.$bus.emit('getStatus');
      this.intervalCount += 1;

      if (this.intervalCount > 10) {
        this.submitLoading = false;
        this.$q.notify({
          color: 'negative',
          position: 'bottom-right',
          message: 'Failed to submit model',
          icon: 'report_problem'
        })
        // @ts-expect-error Bla
        clearInterval(this.timer)
      }
      if (this.status.submitted) {
        this.submitLoading = false;
        if (this.modelData.job.cluster) {
          await sleep(20000);
        } else {
          await sleep(20000);
        }
        this.$bus.emit('enableWebsocket');
        // @ts-expect-error Bla
        clearInterval(this.timer)
      }
    },
    async cancelJob() {

      this.submitLoading = true;
      await cancelJob({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        sbatch: this.modelData.job.sbatch
      })
        .then(() => {
          this.$q.notify({
            message: 'Job canceled'
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

      this.$bus.emit('getStatus');
      this.submitLoading = false;
    },
    async saveResults(allData: boolean) {
      this.resultsLoading = true;

      const params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName,
        output: this.getPlotOutput,
        tasks: this.modelData.job.tasks,
        cluster: this.modelData.job.cluster,
        all_data: allData
      }
      // await getResults(
      //   {
      //     modelName: this.modelStore.selectedModel.file,
      //     modelFolderName: this.modelData.model.modelFolderName,
      //     output: this.getPlotOutput,
      //     tasks: this.modelData.job.tasks,
      //     cluster: this.modelData.job.cluster,
      //     allData: allData
      //   }
      // )
      await api.get('/results/getResults', { params, responseType: 'blob' })
        .then((response) => {
          let filename = this.modelStore.selectedModel.file + '_' + this.modelData.model.modelFolderName + '_' + this.modelData.outputs[0]!.name + '.e'
          if (allData) {
            filename = this.modelStore.selectedModel.file + '_' + this.modelData.model.modelFolderName + '.zip'
          }
          const status: boolean | Error = exportFile(filename, response.data)
          if (status) {
            // browser allowed it
            console.log('ok')
          } else {
            // browser denied it
            console.log(status)
          }
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
      const items = [];

      for (let i = 0; i < this.computes.length; i++) {
        items.push(this.computes[i]!.name);
      }
      items.push('Time');
      this.getPlotVariables = items;
      this.getPlotOutput = this.modelData.outputs[0]!.name
    },
    async _getPlot() {
      this.viewStore.modelLoading = true;

      await getPlot({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        output: this.getPlotOutput,
        tasks: this.modelData.job.tasks
      })
        .then((response) => {
          const plotRawData = response as { [index: string]: number[] }
          this.$q.notify({
            message: 'Plot loaded',
          })

          const tempData = []
          const tempLayout = structuredClone(toRaw(this.viewStore.plotLayout))
          const firstPropety = Object.keys(plotRawData)[0] as string
          let id = 0
          for (const propertyName in plotRawData) {
            if (propertyName != firstPropety) {
              tempData.push({ name: propertyName, x: plotRawData[firstPropety] as number[], y: plotRawData[propertyName] as number[], type: 'scatter', marker: { color: this.color[id] } })
              id += 1
            }
          }
          tempLayout.xaxis.title = firstPropety
          // @ts-expect-error Bla
          tempLayout.title = this.$route.params.id

          this.viewStore.plotData = structuredClone(tempData)
          this.viewStore.plotLayout = structuredClone(tempLayout)

          this.viewStore.viewId = 'plotly';
        })
        .catch((e) => {
          console.log(e)
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
    //     model_name: this.modelStore.selectedModel.file,
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

      // const api = axios.create({ baseURL: 'http://localhost:8080', headers: { 'userName': this.store.username } });

      let materialName = '';
      for (let i = 0; i < this.blocks.length; i++) {
        if (this.blocks[i]!.damageModel != '') {
          materialName = this.blocks[i]!.material!;
        }
      }
      let materialId = 1
      for (let i = 0; i < this.materials.length; i++) {
        if (this.materials[i]!.name == materialName) {
          materialId = i
        }
      }

      let height = 0

      for (let i = 0; i < this.modelStore.modelParams.valves.length; i++) {
        const param = this.modelStore.modelParams.valves[i]!
        if (param.name == 'HEIGHT') {
          height = param.value as number
        }
      }
      console.log(length)

      const params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName,
        height: height,
        crack_length: this.bondFilters[0]!.lowerLeftCornerX! + this.bondFilters[0]!.bottomLength!,
        young_modulus: this.materials[materialId]!.youngsModulus,
        poissions_ratio: this.materials[materialId]!.poissonsRatio,
        yield_stress: this.materials[materialId]!.yieldStress,
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
    async getEnergyReleasePlot() {

      this.viewStore.modelLoading = true;

      // const api = axios.create({ baseURL: 'http://localhost:8080', headers: { 'userName': this.store.username } });
      let thickness = null
      if (this.modelData.model.twoDimensional) {
        thickness = this.damages[0]!.thickness;
      }

      const params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        output_exodus: this.getPlotOutput,
        output_csv: this.getPlotOutputCsv,
        tasks: this.modelData.job.tasks,
        force_output_name: this.getEnergyPlotVariableY + this.getImageAxisSelected.toLowerCase(),
        displacement_output_name: this.getEnergyPlotVariableX + this.getImageAxisSelected.toLowerCase(),
        step: this.getImageStep,
        thickness: thickness,
        // crack_start: this.modelData.bondFilters[0].lowerLeftCornerX + this.modelData.bondFilters[0].bottomLength,
      }
      await api.get('/results/getEnergyReleasePlot', { params, responseType: 'blob' })
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

      this.viewStore.viewId = 'image';
      this.viewStore.modelLoading = false;
    },
    downloadModelImage() {
      const fileLink = document.createElement('a');
      fileLink.href = this.viewStore.modelImg;
      fileLink.setAttribute('download', this.modelStore.selectedModel.file + '.png');
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
    openGetEnfAnalysisDialog() {
      const outputKeys = []
      for (let i = 0; i < this.computes.length; i++) {
        outputKeys.push(this.computes[i]!.name)
      }
      this.computeKeys = outputKeys
      this.dialogGetEnfAnalysis = true;
    },
    async _getEnfAnalysis() {
      this.viewStore.modelLoading = true;

      let length = 0
      let width = 0
      let cracklength = 0

      for (let i = 0; i < this.modelStore.modelParams.valves.length; i++) {
        const param = this.modelStore.modelParams.valves[i]!
        if (param.name == 'LENGTH') {
          length = param.value as number
        }
        if (param.name == 'WIDTH') {
          width = param.value as number
        }
        if (param.name == 'CRACK_LENGTH') {
          cracklength = param.value as number
        }
      }
      console.log(length)

      await getEnfAnalysis({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        length: length,
        width: width,
        crackLength: cracklength,
        cluster: this.modelData.job.cluster,
        tasks: this.modelData.job.tasks,
        output: this.getImageOutput,
        step: this.getImageStep,
        loadVariable: this.getAnalysisVariables[0]!,
        displVariable: this.getAnalysisVariables[1]!
      })
        .then((response) => {
          console.log(response)
          this.viewStore.jsonData = response
          this.viewStore.viewId = 'json';
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
        .then(() => {
          this.$q.notify({
            message: "Model deleted"
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
        .then(() => {
          this.$q.notify({
            message: "Model deleted from cluster"
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
        .then(() => {
          this.$q.notify({
            message: "User data deleted"
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
        .then(() => {
          this.$q.notify({
            message: "User data deleted from cluster"
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

      this.$bus.emit('getStatus');
    },
    csvDefined() {
      for (let i = 0; i < this.modelData.outputs.length; i++) {
        if (this.modelData.outputs[i]!.selectedFileType == 'CSV') {
          return true
        }
      }
      return false
    },
    deleteCookies() {
      localStorage.removeItem('darkMode');
      localStorage.removeItem('modelData');
      localStorage.removeItem('selectedModel');
      localStorage.removeItem('modelParams');
      localStorage.removeItem('panel');
    },
  },
  unmounted() {
    // @ts-expect-error Bla
    clearInterval(this.timer)
  }
})
</script>
