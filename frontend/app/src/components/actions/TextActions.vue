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
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'stores/default-store';
import { useModelStore } from 'stores/model-store';
import { useViewStore } from 'stores/view-store';
import { inject } from 'vue'
import { useQuasar } from 'quasar'
import rules from "assets/rules.js";

export default defineComponent({
  name: "TextActions",
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
      this.getStatus()
    })
  },
  data() {
    return {
      connection: null,
    };
  },
  methods: {
    async viewInputFile(loadFile) {

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        own_mesh: this.modelData.model.ownMesh
      }

      this.$api.get('/model/viewInputFile', { params })
        .then((response) => {
          this.$q.notify({
            message: response.data.message
          })
          this.viewStore.textOutput = response.data.data;
          this.viewStore.textId = "input"
          if (loadFile) {
            this.loadYamlString(response.data.data);
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
      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        input_string: this.viewStore.textOutput
      }

      this.$api.put('/upload/inputFile', '', { params })
        .then((response) => {
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
    async getStatus() {
      console.log("getStatus");

      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        own_model: this.modelData.model.ownModel,
        cluster: this.modelData.job.cluster,
      }

      this.$api.get('/jobs/getStatus', { params })
        .then((response) => {
          this.$q.notify({
            message: response.data.message
          })
          this.store.status = response.data.data
          console.log(this.store.status)
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.data.detail
          })
        })
    },
    async enableWebsocket() {
      // Check if there is an existing connection
      if (this.connection) {
        // Close the existing connection
        await this.connection.close();
        this.connection = null; // Reset the connection variable
      }
      console.log("websocket");
      const params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        token: this.$api.defaults.headers.common['Authorization'],
        user_name: this.$api.defaults.headers.common['userName'],
      };

      const queryString = Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');

      // TODO: socket path wont work on build
      let socket_path = `ws://${window.location.host}/ws?${queryString}`;
      if (window.location.protocol === "https:") {
        socket_path = `wss://${window.location.host}/ws?${queryString}`;
      }
      if (process.env.DEV) {
        socket_path = `ws://localhost:5000/ws?${queryString}`;
      }
      console.log(window.location.protocol)
      console.log(socket_path)
      this.connection = new WebSocket(socket_path);
      this.connection.onmessage = (event) => {
        this.viewStore.logOutput = event.data;
      }
      this.connection.onerror = (event) => {
        console.log(event)
        this.$q.notify({
          type: 'negative',
          message: event
        })
      }
    },
  },
  mounted() {
    this.getStatus();
    this.enableWebsocket();
  },
})
</script>
