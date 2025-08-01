<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-table flat :rows="rows" :columns="columns" row-key="id" :loading="loading" clickable @row-click="onRowClick"
      :rows-per-page-options="[0]">
      <template v-slot:loading>
        <q-inner-loading showing color="primary"></q-inner-loading>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props" @click="onRowClick(props.row)">
            {{ props.row.name + " (" + props.row.sub_name + ")" }}
          </q-td>
          <q-td key="cluster" :props="props">
            <q-badge color="purple">
              {{ props.row.cluster }}
            </q-badge>
          </q-td>
          <q-td key="submitted" :props="props">
            <q-badge :color="props.row.submitted ? 'green' : 'red'">
              {{ props.row.submitted }}
            </q-badge>
          </q-td>
          <q-td key="results" :props="props">
            <q-badge :color="props.row.results ? 'green' : 'red'">
              {{ props.row.results }}
            </q-badge>
          </q-td>
          <q-td key="id" :props="props">
            <q-btn flat icon="fas fa-times" @click="cancelJob(props.row)" :disable="!props.row.submitted">
              <q-tooltip>
                Cancel Job
              </q-tooltip>
            </q-btn>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <!-- <q-btn flat icon="fas fa-times" @click="cancelJob" :disable="selected.length==0">
            <q-tooltip>
                Cancel Job
            </q-tooltip>
        </q-btn> -->
  </div>
</template>

<script>
import { computed, defineComponent, inject } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import { cancelJob, getJobs } from 'src/client';

export default defineComponent({
  name: 'JobsView',
  setup() {
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)
    const viewStore = useViewStore();
    const bus = inject('bus')
    return {
      modelStore,
      modelData,
      viewStore,
      bus
    }
  },
  created() {
    this.bus.on('getJobs', () => {
      this._getJobs()
    })
  },
  data() {
    return {
      loading: false,
      selected: [],
      columns: [
        { name: 'name', label: 'ModelName', field: 'name', sortable: true, align: 'left' },
        { name: 'cluster', label: 'Cluster', field: 'cluster', sortable: true },
        { name: 'submitted', label: 'Submitted', field: 'submitted', sortable: true },
        { name: 'results', label: 'Results', field: 'results', sortable: true },
        // { name: 'created', hidden: true},
        { name: 'id', required: true, hidden: true },
      ],
      rows: [
      ]
    };
  },
  mounted() {
    this._getJobs()
  },
  methods: {
    async cancelJob(row) {
      this.loading = true;

      await cancelJob({
        modelName: row.name,
        modelFolderName: row.sub_name,
        cluster: row.cluster,
        sbatch: true,
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
      this.bus.emit('getStatus')
      this._getJobs();
    },
    onRowClick(row) {
      this.modelStore.modelData = row.model;
      console.log(row.model);
    },
    async _getJobs() {
      this.loading = true;

      await getJobs({ modelName: this.modelStore.selectedModel.file, sbatch: this.modelData.job.sbatch })
        .then((response) => {
          this.rows = response.data
          this.$q.notify({
            message: response.message
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.detail
          })
          this.loading = false;
        })
      this.loading = false;
    },
  },
})
</script>

<style></style>
