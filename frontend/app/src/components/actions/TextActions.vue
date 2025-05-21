<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="row">
    <!-- <q-btn flat icon="fas fa-sync-alt" @click="viewInputFile(false)" :disable="!store.status.created">
      <q-tooltip>
        Reload Inputfile
      </q-tooltip>
    </q-btn> -->
    <q-btn flat icon="fas fa-save" @click="writeInputFile"
      :disable="!store.status.created || viewStore.textId != 'input'">
      <q-tooltip>
        Save Inputfile
      </q-tooltip>
    </q-btn>

    <q-space></q-space>
    <q-toggle class="my-toggle" v-model="debug" label="Debug" standout dense></q-toggle>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { inject } from 'vue'
import { useQuasar } from 'quasar'
import { getStatus, viewInputFile, writeInputFile, OpenAPI } from 'src/client';
import rules from 'assets/rules.js';

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default defineComponent({
  name: 'TextActions',
  setup() {
    const $q = useQuasar()
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
      bus,
    }
  },
  created() {
    this.bus.on('enableWebsocket', (loadFile) => {
      this.enableWebsocket(loadFile)
    })
    this.bus.on('viewInputFile', (loadFile) => {
      this.viewInputFile(loadFile)
    })
    this.bus.on('getStatus', () => {
      this._getStatus()
    })
  },
  beforeDestroy() {
    this.bus.off('enableWebsocket')
    this.bus.off('viewInputFile')
    this.bus.off('getStatus')
  },
  data() {
    return {
      connection: null,
      debug: false,
      lastLine: '',
    };
  },
  methods: {
    async viewInputFile(loadFile) {
      console.log('viewInputFile')

      viewInputFile({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, ownMesh: this.modelData.model.ownMesh })
        .then((response) => {
          this.$q.notify({
            message: response.message
          })
          this.viewStore.textOutput = response.data;
          this.viewStore.textId = 'input'
          if (loadFile) {
            this.loadYamlString(response.data);
          }
        })
        .catch((error) => {
          this.$q.notify({
            color: 'negative',
            position: 'bottom-right',
            message: error,
            icon: 'report_problem'
          })
        })
    },
    writeInputFile() {

      writeInputFile({ modelName: this.modelStore.selectedModel.file, modelFolderName: this.modelData.model.modelFolderName, inputString: this.viewStore.textOutput })
        .then((response) => {
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
    async _getStatus() {
      console.log('getStatus');

      const response = await getStatus({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        ownModel: this.modelData.model.ownModel,
        cluster: this.modelData.job.cluster,
        sbatch: this.modelData.job.sbatch
      });
      console.log(response)
      this.$q.notify({
        message: response.message
      })
      this.store.status = response.data
      // this.$api.get('/jobs/getStatus', { params })
      //   .then((response) => {
      //     this.$q.notify({
      //       message: response.data.message
      //     })
      //     this.store.status = response.data.data
      //     console.log(this.store.status)
      //   })
      //   .catch((error) => {
      //     this.$q.notify({
      //       type: 'negative',
      //       message: error.response.data.detail
      //     })
      //   })
    },
    async enableWebsocket() {
      console.log('enableWebsocket')
      // Check if there is an existing connection
      if (this.connection) {
        // Close the existing connection
        console.log('close existing connection')
        await this.connection.close();
        this.connection = null; // Reset the connection variable
      }
      const params = {
        model_name: this.modelStore.selectedModel.file,
        model_folder_name: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        token: OpenAPI.TOKEN,
        user_name: OpenAPI.HEADERS['userName'],
        debug: this.debug
      };

      const queryString = Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');

      // TODO: socket path wont work on build
      let socket_path = `ws://${window.location.host}/ws?${queryString}`;
      if (window.location.protocol === 'https:') {
        socket_path = `wss://${window.location.host}/ws?${queryString}`;
      }
      if (process.env.DEV) {
        socket_path = `ws://localhost:8000/ws?${queryString}`;
      }
      this.connection = new WebSocket(socket_path);
      this.connection.onmessage = (event) => {
        this.viewStore.logOutput = event.data;
        // get last line and compare
        const lines = this.viewStore.logOutput.split('\n');
        const lastLine = lines[lines.length - 2];
        if (lastLine != this.lastLine) {
          if (lastLine && lastLine.includes('[Info] Run ')) {
            this.viewStore.viewId = 'results';
          }
          if (lastLine && lastLine.includes('[Info] PeriLab finished')) {
            this.connection.close();
            this.connection = null; // Reset the connection variable
            this._getStatus();
            this.bus.emit('getJobs')
            if (this.store.status.submitted) {
              this.$q.notify({
                message: 'PeriLab finished'
              })
            }
          }
          if (lastLine && lastLine.includes('[Error]') ) {
            this.connection.close();
            this.connection = null; // Reset the connection variable
            this._getStatus();
            this.bus.emit('getJobs')
            if (this.store.status.submitted) {
              this.$q.notify({
                color: 'negative',
                message: lastLine
              })
            }
          }
          this.lastLine = lastLine
        }
      }
      this.connection.onerror = (event) => {
        console.log(event)
        this.$q.notify({
          type: 'negative',
          message: event
        })
      }
      this.viewStore.textLoading = false;
    },
  },
  mounted() {
    this._getStatus();
    this.enableWebsocket();
  },
})
</script>
