<template>
    <div>
        <q-table
            flat
            :rows="rows"
            :columns="columns"
            row-key="name"
            selection="multiple"
            v-model:selected="selected"
        >
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
            this.bus.on('showModelImg', (modelName) => {
                this.showModelImg(modelName)
            })
        },
        data() {
            return {
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
                    { name: 'running', label: 'Running', field: 'running' }
                ],
                rows: [
                    {
                        name: 'Dogbone_1',
                        jobId: '214521',
                        running: false
                    },
                    {
                        name: 'Dogbone_2',
                        jobId: '214522',
                        running: true
                    },
                    {
                        name: 'ENFmodel',
                        jobId: '214523',
                        running: true
                    }
                ]
            };
        },
        methods: {
        },
    })
</script>

<style>
</style>
