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
      @change="onFi    lePicked" />
    <input type="file" style="display: none" ref="multifileInput" multiple accept="text/plain,.g"
      @change="onMultiFileP    icked" />
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
          <q-input v-model="gcodeDt" :rules="[r    ules.float]" label="dt" clearable standout></q-input>
          <q-input v-model="gcodeScale" :rules="[rules.float]" label="Scale" clearable standout></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Ok" color="primary" v-close-popup @click="loadGcodeModel"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogTra    nslate" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Translator</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Configurations
          <q-input v-model="translatorD    iscretization" :rules="[rules.fl    oat]" label="Discretization" clearable
            standout></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Ok" color="primary" v-close-popup @click="loadMeshioMo    del"></q-btn>
          <q-btn flat label="Cancel" color="primary" v-close-popup></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-btn flat icon="fas fa-save" @click="saveData">
      <q-tooltip>
        Save as JSON
      </q-tooltip>
    </q-btn>

    <q-btn v-if="!modelData.model.ownMo    del" flat icon="fas fa-undo" @click="bu    s.emit('resetData')">
      <q-tooltip>
        Reset Data
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelData.modelm    odelNameSelected == '    RVE' & !modelData.modelownM    odel" flat icon="fas fa-cogs"
      @click="genera    teMesh">
      <q-tooltip>
        Generate Mesh
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-cogs" @click="generateModel">
      <q-tooltip>
        Generate Model
      </q-tooltip>
    </q-btn>

    <q-btn v-if="mod    elData.model.own    Model" flat icon="fas fa-upload" @click="uploadMesh">
      <q-tooltip>
        Upload Mesh
      </q-tooltip>
    </q-btn>

    <q-btn v-if="modelD    ata.model.ownModel" flat icon="fas fa-upload" @click="u    ploadNodesets">
      <q-tooltip>
        Upload Nodesets
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-download" @click="    saveModel" :disable="!s    tore.status.created">
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

    <q-btn flat icon="fas fa-sort" @click="bus.emit    ('openHidePanels')">
      <q-tooltip>
        Collapse/Expand all panel
      </q-tooltip>
    </q-btn>

    <q-btn flat icon="fas fa-info" @click="bus.em    it('showTutorial')">
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
import rules from "assets/rules.js";

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

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
      this.viewStore.viewId = "model";
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

      if (filetype == "application/json") {
        this.loadJsonFile(fr, file);
      } else if (file.name.includes(".yaml")) {
        this.loadYamlModel(fr, file);
      } else if (file.name.includes(".gcode")) {
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
        formData.append("files", files[i]);
      }

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName
      }

      await this.$api.post('/upload/files', formData, { params })
        .then((response) => {
          if (response.data.data) {
            this.$q.notify({
              message: response.data.message
            })
          }
          else {
            this.$q.notify({
              type: 'negative',
              message: response.data.message
            })
          }
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.data.detail
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

      this.modelStore.modelData.model.modelNameSelected = file.name.split(".")[0];

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

      this.modelStore.modelData.model.modelNameSelected = file.name.split(".")[0];

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
        this.modelStore.modelData.model.modelNameSelected = this.meshioFile.name.split(".")[0];

        await this.translateModel(this.meshioFile, true);
      } else {
        this.viewStore.modelLoading = false;
      }
    },
    async translateModel(file, upload) {
      if (upload) {
        await this.uploadfiles([file]);
      }

      let params = {
        file: file.name,
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        discretization: this.translatorDiscretization,
      }
      console.log(params)
      await this.$api.post('/translate/model', '', { params })
        .then((response) => {
          this.modelStore.modelData.model.meshFile = this.modelData.model.modelNameSelected + ".txt"
          if (response.data.data) {
            this.$q.notify({
              message: response.data.message
            })
            this.viewStore.viewId = "model";
            this.bus.emit('viewPointData');
          }
          else {
            this.$q.notify({
              type: 'negative',
              message: response.data.message
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

      this.modelStore.modelData.model.modelNameSelected = this.gcodeFile.name.split(".")[0];
      const filetype = this.gcodeFile.name.split(".")[1];

      await this.translateGcode(this.gcodeFile, true);
    },
    async translateGcode(file, upload) {
      if (upload) {
        await this.uploadfiles([file]);
      }

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        discretization: this.gcodeDiscretization,
        dt: this.gcodeDt,
        scale: this.gcodeScale
      }

      await this.$api.post('/translate/gcode', '', { params })
        .then((response) => {
          this.modelStore.modelData.model.meshFile = this.modelData.model.modelNameSelected + ".txt"
          this.$q.notify({
            message: response.data.message
          })
          this.viewStore.viewId = "model";
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
        new Blob([JSON.stringify(this.modelData)], { type: "application/json" })
      );
      var fileLink = document.createElement("a");
      fileLink.href = fileURL;
      fileLink.setAttribute("download", this.modelData.model.modelNameSelected + ".json");
      document.body.appendChild(fileLink);
      fileLink.click();
    },
    saveModel() {

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName
      }
      this.$api.get('/model/getModel', { params, responseType: "blob" })
        .then((response) => {
          var fileURL = window.URL.createObjectURL(new Blob([response.data]));
          var fileLink = document.createElement("a");
          fileLink.href = fileURL;
          fileLink.setAttribute("download", this.modelData.model.modelNameSelected + "_" + this.modelData.model.modelFolderName + ".zip");
          document.body.appendChild(fileLink);
          fileLink.click();
          this.$q.notify({
            message: response.data.message
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.data.detail
          })
        })
    },
    async generateModel() {

      if (this.modelData.model.ownModel == false) {
        this.viewStore.modelLoading = true;
      }
      this.viewStore.textLoading = true;

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName
      }

      this.viewStore.viewId = "model";

      await this.$api.post('/generate/model', this.modelData, { params })
        .then((response) => {
          this.$q.notify({
            message: response.data.message
          })
          this.bus.emit("viewInputFile", false)
          if (this.modelData.model.ownModel == false) {
            console.log("generateModel")
            // if (this.viewStore.viewId != "model") {
            this.bus.emit('viewPointData');
            // }
          }
          this.bus.emit("getStatus")
        })
        .catch((error) => {
          let message = "";
          if (error.response != undefined && error.response.status == 422) {
            for (let i in error.response.data.detail) {
              message += error.response.data.detail[i].loc[1] + " ";
              message += error.response.data.detail[i].loc[2] + ", ";
              message += error.response.data.detail[i].loc[3] + ", ";
              message += error.response.data.detail[i].msg + "\n";
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
