<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="flex-center">
    <div v-if="selectedModel.file == ''" class="row justify-center full-width q-pa-md q-my-lg">
      <q-card style="width: 400px">
        <q-card-section v-if="modelList.length > 0">
          <div class="text-h6" style="text-align: center">Select existing model</div>
        </q-card-section>
        <q-select v-if="modelList.length > 0" dense class="q-pa-md" :options="modelList" option-label="title"
          v-model="selectedModel" label="Model" standout @update:model-value="selectModel"></q-select>

        <q-separator inset />
        <q-card-section v-if="modelList.length > 0">
          <div class="text-h6" style="text-align: center">Or</div>
        </q-card-section>
        <q-btn flat icon="fas fa-add" @click="dialogAddModel = true" :disable="store.TRIAL" style="width: 390px"
          label="Add a new Model">
          <q-tooltip v-if="!store.TRIAL">
            Disabled in trial version
          </q-tooltip>
        </q-btn>
      </q-card>
    </div>
    <div v-if="selectedModel.file != ''">
      <q-btn flat icon="fas fa-add" @click="dialogAddModel = true" :disable="store.TRIAL">
        <q-tooltip>
          <div v-if="!store.TRIAL">Add Model</div>
          <div v-if="store.TRIAL">Disabled in trial version</div>
        </q-tooltip>
      </q-btn>
      <q-select class="q-pa-sm" :options="modelList" option-label="title" v-model="selectedModel" label="Model" standout
        dense @update:model-value="selectModel"></q-select>

      <q-splitter v-model="verticalSplitterModel" class="body" :limits="[0, 100]" style="height:calc(100vh - 225px);">
        <template v-slot:before>
          <q-resize-observer @resize="onResizeBefore" :debounce="0" />
          <div v-if="sourceCode != ''">
            <div class="row">
              <q-btn class="q-ma-sm" color="primary" label="Save" @click="_saveModel" />
              <q-btn class="q-ma-sm" color="negative" label="Delete" @click="dialogDeleteModel = true" />
            </div>
            <q-scroll-area :style="{ 'height': modelHeight }">
              <prism-editor class="my-editor" v-model="sourceCode" :highlight="highlighter" line-numbers></prism-editor>
            </q-scroll-area>
          </div>
        </template>

        <template v-slot:after>
          <q-resize-observer @resize="onResizeAfter" :debounce="0" />
          <div v-if="Object.keys(config).length !== 0">
            <div class="row">
              <q-btn class="q-ma-sm" color="primary" label="Save" @click="_saveConfig" />
            </div>
            <q-scroll-area :style="{ 'height': configHeight }">
              <vue-json-pretty :data="config" :editable=true />
              <!-- <JsonEditorVue v-model="config" :mainMenuBar=false :navigationBar=false :statusBar=false :readOnly=false
              v-bind="{/* local props & attrs */ }" /> -->
            </q-scroll-area>
          </div>
        </template>
      </q-splitter>
    </div>

    <q-dialog v-model="dialogAddModel" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Add Model</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input dense v-model="newModelName" label="Model Name" />
          <q-input dense v-model="description" label="Description" />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Create" color="primary" v-close-popup @click="_addModel" />
          <q-btn flat label="Cancel" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogDeleteModel" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Are you sure you want to delete {{ selectedModel.title }}?</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Delete" color="negative" v-close-popup @click="_deleteModel" />
          <q-btn flat label="Cancel" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script lang="ts">

import { useDefaultStore } from 'src/stores/default-store';
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css'; // import the styles somewhere
//@ts-expect-error Bla
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css'; // import syntax highlighting styles
// import JsonEditorVue from 'json-editor-vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';

import { getOwnModels, getOwnModelFile, getConfig, saveConfig, saveModelFile, addModel, deleteModelFile } from '../client';
import type { GetOwnModelsResponse, ModelData } from 'src/client';

export default {
  name: 'CuratorPage',

  components: {
    PrismEditor,
    VueJsonPretty
    // JsonEditorVue
  },
  setup() {
    const store = useDefaultStore();
    return {
      store
    }
  },
  data() {
    return {
      modelList: [] as GetOwnModelsResponse,
      selectedModel: {
        title: '',
        file: '',
      },

      dialogAddModel: false,
      dialogDeleteModel: false,
      newModelName: '',
      description: '',

      sourceCode: '',
      config: {} as ModelData,
      verticalSplitterModel: 50,

      modelHeight: '400px',
      configHeight: '400px',
    };
  },
  methods: {
    onResizeBefore(size: object) {
      if ('height' in size) {
        this.modelHeight = size.height - 60 + 'px'
      }
    },
    onResizeAfter(size: object) {
      if ('height' in size) {
        this.configHeight = size.height - 60 + 'px'
      }
    },
    highlighter(code: string) {
      return highlight(code, languages.py); // languages.<insert language> to return html with markup
    },
    async _addModel() {
      const response = await addModel({
        modelName: this.newModelName,
        description: this.description
      })
      this.selectedModel.title = this.newModelName
      this.selectedModel.file = response
      await this._getModels()
      await this.selectModel()
    },
    async _getModels() {
      const response = await getOwnModels({
        verify: true
      })
      this.modelList = response;
    },
    async selectModel() {
      const response = await getOwnModelFile({
        modelFile: this.selectedModel.file
      })
      this.sourceCode = response
      const config = await getConfig({
        configFile: this.selectedModel.file
      })
      this.config = config as ModelData;
    },
    async _saveModel() {
      await saveModelFile({
        modelFile: this.selectedModel.file,
        sourceCode: this.sourceCode
      }).then(() => this.$q.notify({
        message: 'Model saved',
      })).catch((error) => {
        console.log(error.body.detail)
        this.$q.notify({
          type: 'negative',
          message: error.body.detail
        })
      })
    },
    async _saveConfig() {
      await saveConfig({
        configFile: this.selectedModel.file,
        requestBody: this.config
      }).then(() => this.$q.notify({
        message: 'Config saved',
      })).catch((error) => {
        console.log(error.body.detail)
        for (let i = 0; i < error.body.detail.length; i++) {
          this.$q.notify({
            type: 'negative',
            message: error.body.detail[i].msg + '\n' + error.body.detail[i].loc
          })
        }
      })
    },
    async _deleteModel() {
      await deleteModelFile({
        modelName: this.selectedModel.file,
      }).then(() => {
        this.$q.notify({
          message: 'Model deleted',
        })
        this.sourceCode = ''
        this.config = {}
      })
      await this._getModels()
    }
  },
  async mounted() {
    await this._getModels()
  },
  watch: {
  }
};
</script>
<style>
/* required class */
.my-editor {
  /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
  background: #2d2d2d;
  color: #ccc;

  /* you must provide font-family font-size line-height. Example: */
  font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 5px;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
  outline: none;
}
</style>
