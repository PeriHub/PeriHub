<template>
    <div>
        <q-table
            flat
            :rows="rows"
            :columns="columns"
            row-key="name"
            selection="multiple"
            v-model:selected="selected"
            :loading="loading"
        >
        <template v-slot:loading>
            <q-inner-loading showing color="primary"></q-inner-loading>
        </template>
        </q-table>
            
        <!-- <q-btn flat icon="fas fa-times" @click="cancelJob" :disabled="selected.length==0">
            <q-tooltip>
                Cancel Job
            </q-tooltip>
        </q-btn> -->
    </div>
</template>

<script>
    import { defineComponent, inject } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { useViewStore } from 'stores/view-store';

    export default defineComponent({
        name: 'JobsView',
        setup() {
            const modelStore = useModelStore();
            const viewStore = useViewStore();
            const bus = inject('bus')
            return {
                modelStore,
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
                    {
                        name: 'name',
                        required: true,
                        label: 'ModelName',
                        align: 'left',
                        field: row => row.name,
                        format: val => `${val}`,
                        sortable: true
                    },
                    { name: 'jobId', label: 'JobId', field: 'jobId', sortable: true },
                    { name: 'cluster', label: 'Cluster', field: 'cluster', sortable: true },
                    { name: 'created', label: 'Created', field: 'created', sortable: true },
                    { name: 'submitted', label: 'Submitted', field: 'submitted', sortable: true },
                    { name: 'results', label: 'Results', field: 'results', sortable: true }
                ],
                rows: [
                    {
                        name: "ENFmodel",
                        job_id: "",
                        cluster: "Cara",
                        created: true,
                        submitted: false,
                        results: true
                    }
                ]
            };
        },
        mounted(){
            this.getJobs()
        },
        methods: {
            async getJobs() {
                this.loading = true;
                await this.$api.get('/getJobs')
                .then((response) => {
                    this.rows = response.data.data
                    this.$q.notify({
                        message: response.data.message
                    })
                })
                .catch( (error)=> {
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

<style>
</style>
