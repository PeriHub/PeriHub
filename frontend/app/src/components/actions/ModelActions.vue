<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <q-btn flat icon="fas fa-upload" @click="readData" :disable="store.TRIAL">
      <q-tooltip>
        <div v-if="!store.TRIAL">Load Model</div>
        <div v-if="store.TRIAL">Disabled in trial version</div>
      </q-tooltip>
    </q-btn>
    <input type="file" style="display: none" ref="fileInput" accept="application/json" @change="onFilePicked" />

    <q-btn flat icon="fas fa-save" @click="saveData">
      <q-tooltip>
        Save as JSON
      </q-tooltip>
    </q-btn>

    <q-btn v-if="store.DEV" flat icon="fas fa-save" @click="_saveConfig">
      <q-tooltip>
        Save Config
      </q-tooltip>
    </q-btn>

    <q-btn v-if="!modelData.model.ownModel" flat icon="fas fa-undo" @click="bus.emit('resetData')">
      <q-tooltip>
        Reset Data
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-cogs" @click="generateModel">
      <q-tooltip>
        Generate Model
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" flat icon="fas fa-upload" @click="dialogUpload = true"
      :disable="store.TRIAL">
      <q-tooltip>
        <div v-if="!store.TRIAL">Upload Modelfiles</div>
        <div v-if="store.TRIAL">Disabled in trial version</div>
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-download" @click="saveModel" :loading="modelLoading"
      :disable="modelLoading || !store.status.created">
      <q-tooltip>
        Download Modelfiles
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" flat icon="fas fa-backward" @click="switchModels">
      <q-tooltip>
        Use predefined Models
      </q-tooltip>
    </q-btn>

    <q-space></q-space>

    <q-btn flat icon="fas fa-sort" @click="bus.emit('openHidePanels')">
      <q-tooltip>
        Collapse/Expand all panel
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-info" @click="bus.emit('showTutorial')">
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
            :url="uploadPath + '?model_name=' + this.modelStore.selectedModel.file + '&model_folder_name=' + this.modelData.model.modelFolderName"
            :headers="[{ name: 'username', value: store.username }]" field-name="files" label="Pick file" filled counter
            multiple style="max-width: 300px" @uploaded="uploadFinished" /> <!--max-file-size="2097152"  -->
        </q-card-section>
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
import { exportFile } from 'quasar'
import { api } from 'boot/axios';
import { uploadFiles, getModel, generateModel, saveConfig } from 'src/client';
import rules from 'assets/rules.js';

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
  name: 'ModelActions',
  setup() {
    const store = useDefaultStore();
    const modelStore = useModelStore();
    const viewStore = useViewStore();
    const modelData = computed(() => modelStore.modelData)
    const bus = inject('bus')
    const uploadPath = process.env.API + '/upload/files'

    return {
      store,
      viewStore,
      modelStore,
      modelData,
      rules,
      bus,
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
      this.modelStore.modelData.model.gcode = false;
    },
    readData() {
      this.$refs.fileInput.click();
    },
    uploadMesh() {
      this.$refs.meshInput.click();
    },
    uploadNodesets() {
      this.$refs.nodesetsInput.click();
    },
    async uploadFinished(res) {
      this.$q.notify({
        message: 'Files uploaded'
      })
      this.dialogUpload = false
      const type = res.files[0].name.split('.')[1]
      console.log(type)
      if (type == 'gcode') {
        this.modelStore.modelData.model.meshFile = res.files[0].name
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
        this.bus.emit('viewPointData');
      } else if (type == 'txt') {
        if (JSON.parse(res.xhr.response).message != '') {
          this.modelStore.modelData.model.meshFile = res.files[0].name
          this.modelStore.modelData.discretization.discType = 'txt'
        }
        this.viewStore.modelLoading = true;
        this.viewStore.viewId = 'model';
        await sleep(500)
        this.bus.emit('viewPointData');
      }
      this.bus.emit('getStatus')
      this.viewStore.modelLoading = false;
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
    //       this.bus.emit('addCondition')
    //     }
    //     this.modelStore.modelData.boundaryConditions.nodeSets[i].file = files[i].name
    //   }

    //   this.viewStore.modelLoading = false;
    // },
    onFilePicked(event) {
      const file = event.target.files[0];
      const filetype = file.type;
      if (file.length <= 0) {
        return false;
      }

      const fr = new FileReader();

      if (filetype == 'application/json') {
        this.loadJsonFile(fr, file);
      } else if (file.name.includes('.yaml')) {
        this.loadYamlModel(fr, file);
      }
    },
    onMultiFilePicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.viewStore.modelLoading = true;
      this._uploadfiles(files);

      this.viewStore.modelLoading = false;
    },
    loadJsonFile(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = false;
      this.modelStore.modelData.model.gcode = false;

      fr.onload = (e) => {
        const result = JSON.parse(e.target.result);
        this.modelStore.modelData = structuredClone(result)
        const filename = file.name.split('.')[0]
        if (this.modelStore.modelData.model.ownModel) {
          this.modelStore.selectedModel.file = filename;
        }
      };
      fr.readAsText(file);
    },
    loadYamlModel(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      this.modelStore.modelData.model.gcode = false;

      this.modelStore.selectedModel.file = file.name.split('.')[0];

      fr.onload = (e) => {
        const yaml = e.target.result;
        this.loadYamlString(yaml);
      };
      fr.readAsText(file);
    },
    loadXmlModel(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      this.modelStore.modelData.model.gcode = false;

      this.modelStore.selectedModel.file = file.name.split('.')[0];

      fr.onload = (e) => {
        const xml = e.target.result;
        var yaml = this.translateXMLtoYAML(xml);
        this.loadYamlString(yaml);
      };
      fr.readAsText(file);
    },
    saveData() {
      exportFile(this.modelStore.selectedModel.file + '.json', JSON.stringify(this.modelData))
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
      let params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName
      }
      // getModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName })
      await api.get('/model/getModel', { params, responseType: 'blob' })
        .then((response) => {
          let filename = this.modelStore.selectedModel.file + '_' + this.modelData.model.modelFolderName + '.zip'
          const status = exportFile(filename, response.data)
          if (status) {
            // browser allowed it
            console.log('ok')
          } else {
            // browser denied it
            console.log('Error: ' + status)
            this.$q.notify({
              message: 'Error: ' + status
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
        'model_data': this.modelData,
        'valves': this.modelStore.modelParams
      }

      await generateModel({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        requestBody: body
      })
        .then((response) => {
          console.log('generateModel')
          this.$q.notify({
            message: response.message
          })
          this.bus.emit('viewInputFile', false)
          if (this.modelData.model.ownModel == false) {
            // if (this.viewStore.viewId != 'model') {
            this.bus.emit('viewPointData');
            // }
          }
          this.bus.emit('getStatus')
          this.bus.emit('getJobFolders')
        })
        .catch((error) => {
          error = JSON.parse(JSON.stringify(error))
          console.log(error)
          // console.log(error.response)
          // console.log(error.response.status)
          if (error != undefined && error.status == 422) {
            for (let i in error.body.detail) {
              let message = '';
              message += error.body.detail[i].msg + ' ';
              for (let j in error.body.detail[i].loc) {
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
      var color = 'gray';
      if (this.$cookie.get('darkMode') == 'true') {
        color = 'gray';
      } else {
        color = 'white';
      }
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
.q-btn {
  padding-right: 5px;
}
</style>
