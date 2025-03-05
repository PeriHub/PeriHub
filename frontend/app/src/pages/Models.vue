<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="flex-center" style="height:100vh;">
    <q-btn flat icon="fas fa-add" @click="dialogAddModel = true" />
    <q-select class="q-pa-sm" :options="modelList" option-label="title" v-model="selectedModel" label="Model" standout
      dense @update:model-value="selectModel"></q-select>

    <q-splitter v-model="verticalSplitterModel" class="body" :limits="[0, 100]" style="height:calc(100vh - 225px);">
      <template v-slot:before>
        <q-scroll-area style="height:100%;">
          <div v-if="sourceCode != ''">
            <prism-editor class="my-editor" v-model="sourceCode" :highlight="highlighter" line-numbers></prism-editor>
            <q-btn class="q-mt-sm" color="primary" label="Save" @click="_saveModel" />
            <q-btn class="q-mt-sm" color="negative" label="Delete" @click="dialogDeleteModel = true" />
          </div>
        </q-scroll-area>
      </template>

      <template v-slot:after>
        <q-scroll-area style="height:100%;">
          <div v-if="config">
            <JsonEditorVue v-model="config" mode="tree" :mainMenuBar=false :navigationBar=false :statusBar=false
              :readOnly=true v-bind="{/* local props & attrs */ }" />
            <q-btn class="q-mt-sm" color="primary" label="Save" @click="_saveConfig" />
          </div>
        </q-scroll-area>
      </template>
    </q-splitter>

    <q-dialog v-model="dialogAddModel" persistent max-width="800">
      <q-card>
        <q-card-section>
          <div class="text-h6">Add Model</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input dense v-model="newModelName" label="Model Name" />
          <q-input dense v-model="model.description" label="Description" />
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

<script>

import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css'; // import the styles somewhere
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css'; // import syntax highlighting styles
import JsonEditorVue from 'json-editor-vue'

import { getOwnModels, getOwnModelFile, getConfig, saveConfig, saveModel, addModel, deleteModel } from '../client';

export default {
  name: 'CuratorPage',

  components: {
    PrismEditor,
    JsonEditorVue
  },
  data() {
    return {
      modelList: [],
      selectedModel: {
        title: '',
        file: '',
      },

      dialogAddModel: false,
      dialogDeleteModel: false,
      newModelName: '',

      sourceCode: '',
      config: null,
      verticalSplitterModel: 50,
    };
  },
  methods: {
    highlighter(code) {
      return highlight(code, languages.py); // languages.<insert language> to return html with markup
    },
    async _addModel() {
      const response = await addModel({
        modelName: this.newModelName,
        requestBody: this.model
      })
      this.selectedModel.title = this.newMethodName
      this.selectedModel.file = response
      this._getModels()
      this.selectModel()
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
      this.config = config;
    },
    async _saveModel() {
      await saveModel({
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
        configFile: this.selectedModel.config,
        requestBody: this.config
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
    async _deleteModel() {
      await deleteModel({
        modelName: this.selectedModel.title,
      }).then(() => {
        this.$q.notify({
          message: 'Model deleted',
        })
        this.sourceCode = ''
        this._getModels()
      })
    }
  },
  mounted() {
    this._getModels()
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
