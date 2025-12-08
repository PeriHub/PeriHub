<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <q-btn class="action-btn" flat icon="fas fa-upload" @click="readData" :disable="store.TRIAL">
      <q-tooltip>
        <div v-if="!store.TRIAL">Load Model</div>
        <div v-if="store.TRIAL">Disabled in trial version</div>
      </q-tooltip>
    </q-btn>
    <input type="file" style="display: none" ref="fileInput" accept="application/json" @change="onFilePicked" />

    <q-btn class="action-btn" flat icon="fas fa-save" @click="saveData">
      <q-tooltip>
        Save as JSON
      </q-tooltip>
    </q-btn>

    <q-btn v-if="store.DEV" class="action-btn" flat icon="fas fa-save" @click="_saveConfig">
      <q-tooltip>
        Save Config
      </q-tooltip>
    </q-btn>

    <q-btn v-if="!modelData.model.ownModel" class="action-btn" flat icon="fas fa-undo" @click="$bus.emit('resetData')">
      <q-tooltip>
        Reset Data
      </q-tooltip>
    </q-btn>

    <q-btn class="action-btn" flat icon="fas fa-cogs" @click="generateModel">
      <q-tooltip>
        Generate Model
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" class="action-btn" flat icon="fas fa-upload" @click="dialogUpload = true"
      :disable="store.TRIAL">
      <q-tooltip>
        <div v-if="!store.TRIAL">Upload Modelfiles</div>
        <div v-if="store.TRIAL">Disabled in trial version</div>
      </q-tooltip>
    </q-btn>

    <q-btn class="action-btn" flat icon="fas fa-download" @click="saveModel" :loading="modelLoading"
      :disable="modelLoading || !status.created">
      <q-tooltip>
        Download Modelfiles
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" class="action-btn" flat icon="fas fa-backward" @click="switchModels">
      <q-tooltip>
        Use predefined Models
      </q-tooltip>
    </q-btn>

    <q-space></q-space>

    <q-btn class="action-btn" flat icon="fas fa-sort" @click="$bus.emit('openHidePanels')">
      <q-tooltip>
        Collapse/Expand all panel
      </q-tooltip>
    </q-btn>

    <q-btn class="action-btn" flat icon="fas fa-info" @click="$bus.emit('showTutorial')">
      <q-tooltip>
        Show Tutorial
      </q-tooltip>
    </q-btn>
    <q-dialog v-model="dialogUpload" style="max-width: 200px">
      <q-card>
        <q-card-section>
          <div class="text-h6">Upload Data</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-uploader
            :url="uploadPath + '?model_name=' + modelStore.selectedModel.file + '&model_folder_name=' + modelData.model.modelFolderName"
            :headers="[{ name: 'username', value: store.username }]" field-name="files" label="Pick file" filled counter
            multiple style="max-width: 300px" @uploaded="uploadFinished" @failed="uploadFailed" />
          <!--max-file-size="2097152"  -->
        </q-card-section>
      </q-card>
    </q-dialog>

  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { exportFile } from 'quasar'
import { api } from 'boot/axios';
import { generateModel, saveConfig } from 'src/client';
import type { Discretization, ModelData } from 'src/client';
import rules from 'assets/rules.js';
import Driver from 'driver.js';

const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
  name: 'ModelActions',
  setup() {
    const store = useDefaultStore();
    const status = store.status;
    const modelStore = useModelStore();
    const viewStore = useViewStore();
    const modelData = computed(() => modelStore.modelData)
    const uploadPath = process.env.API + '/upload/files'

    return {
      store,
      status,
      viewStore,
      modelStore,
      modelData,
      rules,
      uploadPath
    }
  },
  data() {
    return {
      dialogUpload: false,
      modelLoading: false,
    };
  },
  methods: {
    switchModels() {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = false;
    },
    readData() {
      // @ts-expect-error Bla
      this.$refs.fileInput.click();
    },
    uploadMesh() {
      // @ts-expect-error Bla
      this.$refs.meshInput.click();
    },
    uploadNodesets() {
      // @ts-expect-error Bla
      this.$refs.nodesetsInput.click();
    },
    // @ts-expect-error Bla
    async uploadFinished(res) {
      this.$q.notify({
        message: 'Files uploaded'
      })
      this.dialogUpload = false
      const type = res.files[0]!.name.split('.')[1]
      console.log(type)
      if (type == 'gcode') {
        this.modelStore.modelData.model.meshFile = res.files[0]!.name
        if (!this.modelStore.modelData.discretization) {
          this.modelStore.modelData.discretization = {} as Discretization
        }
        this.modelStore.modelData.discretization.discType = 'gcode'
        if (!this.modelStore.modelData.discretization.gcode) {
          this.modelStore.modelData.discretization.gcode = {
            overwriteMesh: true,
            sampling: 1,
            width: 0.4,
            height: 0.2,
            scale: 1,
          }
        }
      } else if (type == 'g') {
        this.viewStore.modelLoading = true;
        this.viewStore.viewId = 'model';
        await sleep(500)
        this.$bus.emit('viewPointData');
      } else if (type == 'txt') {
        if (JSON.parse(res.xhr.response).message != '') {
          this.modelStore.modelData.model.meshFile = res.files[0]!.name
          if (!this.modelStore.modelData.discretization) {
            this.modelStore.modelData.discretization = {} as Discretization
          }
          this.modelStore.modelData.discretization.discType = 'txt'
        }
        this.viewStore.modelLoading = true;
        this.viewStore.viewId = 'model';
        await sleep(500)
        this.$bus.emit('viewPointData');
      }
      this.$bus.emit('getStatus')
      this.viewStore.modelLoading = false;
    },
    // @ts-expect-error Bla
    uploadFailed(res) {
      console.log(res)
      this.$q.notify({
        message: 'Upload failed, file type not supported!',
        type: 'negative'
      })
    },
    // onNodesetsPicked(event) {
    //   const files = event.target.files;
    //   const filetype = files[0].type;
    //   if (files.length <= 0) {
    //     return false;
    //   }

    //   this.viewStore.modelLoading = true;
    //   this._uploadfiles(files);

    //   for (var i = 0; i < files.length; i++) {
    //     if (this.modelStore.modelData.boundaryConditions.conditions.length < i + 1) {
    //       this.$bus.emit('addCondition')
    //     }
    //     this.modelStore.modelData.boundaryConditions.nodeSets[i].file = files[i].name
    //   }

    //   this.viewStore.modelLoading = false;
    // },
    onFilePicked(event: Event) {
      // @ts-expect-error Bla
      const file = event.target.files[0];
      const filetype = file.type;
      if (file.length <= 0) {
        return false;
      }

      const fr = new FileReader();

      if (filetype == 'application/json') {
        this.loadJsonFile(fr, file);
      }
    },
    loadJsonFile(fr: FileReader, file: Blob) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = false;

      fr.onload = (e) => {
        // @ts-expect-error Bla
        const result = JSON.parse(e.target.result);
        console.log(result)
        if (result.modelData) {
          this.modelStore.modelData = { ...this.modelStore.modelData, ...result.modelData } as ModelData
        } else {
          this.modelStore.modelData = { ...this.modelStore.modelData, ...result } as ModelData
          console.log('Deprecated Json Format!')
        }
        if (result.modelParams) {
          this.modelStore.modelParams = structuredClone(result.modelParams)
        }
        if (result.selectedModel) {
          this.modelStore.selectedModel = structuredClone(result.selectedModel)
        }
        // const filename = file.name.split('.')[0]
        // if (this.modelStore.modelData.model.ownModel) {
        //   this.modelStore.selectedModel.file = filename;
        // }
      };
      fr.readAsText(file);
    },
    saveData() {
      exportFile(this.modelStore.selectedModel.file + '.json', '{"modelData":' + JSON.stringify(this.modelStore.modelData) + ',"modelParams":' + JSON.stringify(this.modelStore.modelParams) + ',"selectedModel":' + JSON.stringify(this.modelStore.selectedModel) + '}');
    },
    async _saveConfig() {
      await saveConfig({
        configFile: this.modelStore.selectedModel.file,
        requestBody: this.modelData,
      }).then(() => this.$q.notify({
        message: 'Config saved',
      })).catch((error) => {
        console.log(error.body.detail)
        this.$q.notify({
          type: 'negative',
          message: error.body.detail
        })
      })
    },
    async saveModel() {
      this.modelLoading = true;
      const params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName
      }
      // getModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName })
      await api.get('/model/getModel', { params, responseType: 'blob' })
        .then((response) => {
          const filename = this.modelStore.selectedModel.file + '_' + this.modelData.model.modelFolderName + '.zip'
          const status = exportFile(filename, response.data)
          if (status) {
            // browser allowed it
            console.log('ok')
          } else {
            // browser denied it
            console.log(status)
            this.$q.notify({
              message: status
            })
          }
        })
        .catch((error) => {
          console.log(error)
          this.$q.notify({
            type: 'negative',
            message: error
          })
        })
      this.modelLoading = false;
    },
    async generateModel() {

      if (this.modelData.model.ownModel == false) {
        this.viewStore.modelLoading = true;
      }
      this.viewStore.textLoading = true;

      this.viewStore.viewId = 'model';

      const body = {
        'data': this.modelData,
        'valves': this.modelStore.modelParams
      }

      await generateModel({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        requestBody: body
      })
        .then(() => {
          console.log('generateModel')
          this.$q.notify({
            message: 'Model generated'
          })
          this.$bus.emit('viewInputFile')
          if (this.modelData.model.ownModel == false) {
            // if (this.viewStore.viewId != 'model') {
            this.$bus.emit('viewPointData');
            // }
          }
          this.$bus.emit('getStatus')
          this.$bus.emit('getJobFolders')
        })
        .catch((error) => {
          error = JSON.parse(JSON.stringify(error))
          console.log(error)
          // console.log(error.response)
          // console.log(error.response.status)
          if (error != undefined && error.status == 422) {
            for (const i in error.body.detail) {
              let message = '';
              message += error.body.detail[i].msg + ' ';
              for (const j in error.body.detail[i].loc) {
                message += error.body.detail[i].loc[j] + ', ';
              }
              this.$q.notify({
                color: 'negative',
                position: 'bottom-right',
                message: message,
                icon: 'report_problem',
                timeout: 0,
                actions: [{ icon: 'close', color: 'white' }]
              })
            }
          }
          else {
            this.$q.notify({
              color: 'negative',
              message: error.body.detail,
              icon: 'report_problem'
            })
          }
        })

      this.viewStore.modelLoading = false;
      this.viewStore.textLoading = false;
    },
    showTutorial() {
      let color = 'gray';
      // @ts-expect-error Bla
      if (this.$cookie.get('darkMode') == 'true') {
        color = 'gray';
      } else {
        color = 'white';
      }
      // @ts-expect-error Bla
      console.log(this.$cookie.get('darkMode'));
      console.log(color);

      const driver = new Driver({
        animate: true, // Animate while changing highlighted element
        opacity: 0.5,
        stageBackground: color,
      });

      // Define the steps for introduction
      driver.defineSteps([
        {
          element: '#model-configuration',
          popover: {
            className: 'first-step-popover-class',
            title: 'Title on Popover',
            description: 'Body of the popover',
            position: 'right',
          },
        },
        {
          element: '#model-output',
          popover: {
            title: 'Title on Popover',
            description: 'Body of the popover',
            position: 'left',
          },
        },
        {
          element: '#button-runModel',
          popover: {
            title: 'Title on Popover',
            description: 'Body of the popover',
            position: 'bottom',
          },
        },
      ]);

      // Start the introduction
      driver.start();
    },
  }
})
</script>
<style>
.action-btn {
  padding-right: 5px;
}
</style>
