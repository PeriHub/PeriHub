<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div>
        <q-table flat :rows="rows" :columns="columns" row-key="id" :loading="loading" clickable @row-click="onRowClick">
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
import { useModelStore } from 'stores/model-store';
import { useViewStore } from 'stores/view-store';

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
            this.getJobs()
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
                // {
                //     id: 1,
                //     name: "ENFmodel",
                //     sub_name: "_1",
                //     cluster: "Cara",
                //     created: true,
                //     submitted: false,
                //     results: true,
                //     model: {}
                // }
            ]
        };
    },
    mounted() {
        this.getJobs()
    },
    methods: {
        async cancelJob(row) {
            this.loading = true;

            let params = {
                model_name: row.name,
                model_folder_name: row.sub_name,
                cluster: row.cluster
            }
            await this.$api.put('/jobs/cancel', '', { params })
                .then((response) => {
                    this.$q.notify({
                        message: response.data.message
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
            this.bus.emit("getStatus")
            this.getJobs();
        },
        onRowClick(row) {
            this.modelStore.modelData = row.model;
            console.log(row.model);
        },
        async getJobs() {
            this.loading = true;
            let params = {
                model_name: this.modelData.model.modelNameSelected,
            }

            await this.$api.get('/jobs/getJobs', { params })
                .then((response) => {
                    this.rows = response.data.data
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
            this.loading = false;
        },
    },
})
</script>

<style></style>
