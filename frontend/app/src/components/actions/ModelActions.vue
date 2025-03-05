<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <q-btn flat icon="fas fa-upload" @click="readData">
      <q-tooltip>
        Load Model
      </q-tooltip>
    </q-btn>
    <input type="file" style="display: none" ref="fileInput" accept="application/json,.yaml,.cdb,.inp,.gcode,.obj"
      @change="onFilePicked" />
    <input type="file" style="display: none" ref="multifileInput" multiple accept="text/plain,.g"
      @change="onMultiFilePicked" />
    <input type="file" style="display: none" ref="meshInput" accept="text/plain,.g" @change="onMeshPicked" />
    <input type="file" style="display: none" ref="nodesetsInput" multiple accept="text/plain,.g"
      @change="onNodesetsPicked" />
    <q-dialog v-model="dialogGcode" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Gcode Translator</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Configurations
          <q-input v-model="gcodeDiscretization" :rules="[rules.float]" label="Discretization" clearable
            standout></q-input>
          <q-input v-model="gcodeDt" :rules="[rules.float]" label="dt" clearable standout></q-input>
          <q-input v-model="gcodeScale" :rules="[rules.float]" label="Scale" clearable standout></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Ok" color="primary" v-close-popup @click="loadGcodeModel"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogTranslate" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Translator</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Configurations
          <q-input v-model="translatorDiscretization" :rules="[rules.float]" label="Discretization" clearable
            standout></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Ok" color="primary" v-close-popup @click="loadMeshioModel"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn flat icon="fas fa-save" @click="saveData">
      <q-tooltip>
        Save as JSON
      </q-tooltip>
    </q-btn>

    <q-btn v-if="!modelData.model.ownModel" flat icon="fas fa-undo" @click="bus.emit('resetData')">
      <q-tooltip>
        Reset Data
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.modelmodelNameSelected == 'RVE' & !modelData.modelownModel" flat icon="fas fa-cogs"
      @click="generateMesh">
      <q-tooltip>
        Generate Mesh
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-cogs" @click="generateModel">
      <q-tooltip>
        Generate Model
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" flat icon="fas fa-upload" @click="uploadMesh">
      <q-tooltip>
        Upload Mesh
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.model.ownModel" flat icon="fas fa-upload" @click="uploadNodesets">
      <q-tooltip>
        Upload Nodesets
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-download" @click="saveModel" :disable="!store.status.created">
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
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { inject } from 'vue'
import { uploadFiles, translateModel, translateGcode, getModel, generateModel } from 'src/client';
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

    return {
      store,
      viewStore,
      modelStore,
      modelData,
      rules,
      bus
    }
  },
  data() {
    return {
      dialogGcode: false,
      gcodeDiscretization: 1,
      gcodeDt: 0.02,
      gcodeScale: 0.001,
      gcodeFile: undefined,
      dialogTranslate: false,
      translatorDiscretization: 1,
      meshioFile: undefined,
    };
  },
  methods: {
    switchModels() {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = false;
      this.modelStore.modelData.model.translated = false;
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
    async onMeshPicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.viewStore.modelLoading = true;
      await this.uploadfiles(files);

      this.modelStore.modelData.model.modelNameSelected = files[0].name.split('.')[0]
      this.modelStore.modelData.model.mesh_file = files[0].name
      this.viewStore.viewId = 'model';
      await sleep(500)
      this.bus.emit('viewPointData');
      this.viewStore.modelLoading = false;
    },
    onNodesetsPicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.viewStore.modelLoading = true;
      this.uploadfiles(files);

      for (var i = 0; i < files.length; i++) {
        if (this.modelStore.modelData.boundaryConditions.conditions.length < i + 1) {
          this.bus.emit('addCondition')
        }
        this.modelStore.modelData.boundaryConditions.nodeSets[i].file = files[i].name
      }

      this.viewStore.modelLoading = false;
    },
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
      } else if (file.name.includes('.gcode')) {
        this.gcodeFile = file;
        this.dialogGcode = true;
      } else {
        this.meshioFile = file;
        this.dialogTranslate = true;
      }
    },
    onMultiFilePicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.viewStore.modelLoading = true;
      this.uploadfiles(files);

      this.viewStore.modelLoading = false;
    },
    async uploadfiles(files) {
      const formData = new FormData();
      for (var i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      await uploadFiles({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, formData: formData })
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
          this.$q.notify({
            type: 'negative',
            message: error.response.detail
          })
        })
    },
    loadJsonFile(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = false;
      this.modelStore.modelData.model.translated = false;

      fr.onload = (e) => {
        const result = JSON.parse(e.target.result);
        this.modelStore.modelData = structuredClone(result)
      };
      fr.readAsText(file);
    },
    loadYamlModel(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      this.modelStore.modelData.model.translated = false;

      this.modelStore.modelData.model.modelNameSelected = file.name.split('.')[0];

      fr.onload = (e) => {
        const yaml = e.target.result;
        this.loadYamlString(yaml);
      };
      fr.readAsText(file);
    },
    loadXmlModel(fr, file) {
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      this.modelStore.modelData.model.translated = false;

      this.modelStore.modelData.model.modelNameSelected = file.name.split('.')[0];

      fr.onload = (e) => {
        const xml = e.target.result;
        var yaml = this.translateXMLtoYAML(xml);
        this.loadYamlString(yaml);
      };
      fr.readAsText(file);
    },
    async loadMeshioModel() {
      this.dialogTranslate = false;
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      this.modelStore.modelData.model.translated = false;
      this.modelStore.modelData.model.twoDimensional = false;

      this.viewStore.modelLoading = true;

      if (this.meshioFile == undefined) {
        return false;
      }

      // if (await this.checkFeSize(file)) {
      if (true) {
        this.modelStore.selectedModel.file = this.meshioFile.name.split('.')[0];

        await this.translateModel(this.meshioFile, true);
      } else {
        this.viewStore.modelLoading = false;
      }
    },
    async translateModel(file, upload) {
      if (upload) {
        await this.uploadfiles([file]);
      }

      await translateModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, discretization: this.translatorDiscretization })
        .then((response) => {
          this.modelStore.modelData.model.meshFile = this.modelData.model.modelNameSelected + '.txt'
          if (response.data) {
            this.$q.notify({
              message: response.message
            })
            this.viewStore.viewId = 'model';
            this.bus.emit('viewPointData');
          }
          else {
            this.$q.notify({
              type: 'negative',
              message: response.message
            })
          }
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.message
          })
          this.viewStore.modelLoading = false;
        })

      this.viewStore.modelLoading = false;
    },
    async loadGcodeModel() {
      this.dialogGcode = false;
      this.modelStore.modelData.model.ownMesh = false;
      this.modelStore.modelData.model.ownModel = true;
      // this.modelStore.modelData.model.translated = true;

      this.viewStore.modelLoading = true;

      if (this.gcodeFile == undefined) {
        return false;
      }

      this.modelStore.modelData.model.modelNameSelected = this.gcodeFile.name.split('.')[0];
      const filetype = this.gcodeFile.name.split('.')[1];

      await this.translateGcode(this.gcodeFile, true);
    },
    async translateGcode(file, upload) {
      if (upload) {
        await this.uploadfiles([file]);
      }

      await translateGcode({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, discretization: this.gcodeDiscretization, dt: this.gcodeDt, scale: this.gcodeScale })
        .then((response) => {
          this.modelStore.modelData.model.meshFile = this.modelData.model.modelNameSelected + '.txt'
          this.$q.notify({
            message: response.message
          })
          this.viewStore.viewId = 'model';
          this.bus.emit('viewPointData');
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.message
          })
          this.viewStore.modelLoading = false;
        })

      this.viewStore.modelLoading = false;
    },
    saveData() {
      var fileURL = window.URL.createObjectURL(
        new Blob([JSON.stringify(this.modelData)], { type: 'application/json' })
      );
      var fileLink = document.createElement('a');
      fileLink.href = fileURL;
      fileLink.setAttribute('download', this.modelData.model.modelNameSelected + '.json');
      document.body.appendChild(fileLink);
      fileLink.click();
    },
    saveModel() {

      getModel({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName })
        .then((response) => {
          var fileURL = window.URL.createObjectURL(new Blob([response.data]));
          var fileLink = document.createElement('a');
          fileLink.href = fileURL;
          fileLink.setAttribute('download', this.modelData.model.modelNameSelected + '_' + this.modelData.model.modelFolderName + '.zip');
          document.body.appendChild(fileLink);
          fileLink.click();
          this.$q.notify({
            message: response.message
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.detail
          })
        })
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
        })
        .catch((error) => {
          console.log(error)
          let message = '';
          if (error.response != undefined && error.response.status == 422) {
            for (let i in error.response.detail) {
              message += error.response.detail[i].loc[1] + ' ';
              message += error.response.detail[i].loc[2] + ', ';
              message += error.response.detail[i].loc[3] + ', ';
              message += error.response.detail[i].msg + '\n';
            }
            message = message.slice(0, -2);
          }
          else {
            message = error.message
          }
          this.$q.notify({
            color: 'negative',
            position: 'bottom-right',
            message: message,
            icon: 'report_problem'
          })
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
  },
})
</script>
<style>
.q-btn {
  padding-right: 5px;
}
</style>
