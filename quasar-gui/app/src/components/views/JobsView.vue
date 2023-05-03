<template>
    <div>
        <q-list
            v-for="block in blocks"
            :key="block.blocksId"
            style="padding: 0px"
        >
            <div class="row my-row">
                <q-input 
                    class="my-input"
                    v-model="block.name"
                    :rules="[rules.required, rules.name]"
                    :label="blockKeys.name"
                    standout
                    dense
                ></q-input>
                <q-select 
                    class="my-select"
                    :options="materials"
                    option-label="name"
                    option-value="name"
                    emit-value
                    v-model="block.material"
                    :label="blockKeys.material"
                    standout
                    dense
                ></q-select>
                <q-select 
                    class="my-select"
                    :options="damages"
                    option-label="name"
                    option-value="name"
                    emit-value
                    v-model="block.damageModel"
                    :label="blockKeys.damageModel"
                    clearable
                    standout
                    dense
                ></q-select>
                <q-select 
                    v-if="additive.enabled"
                    class="my-select"
                    :options="additive.additiveModels"
                    option-label="name"
                    option-value="name"
                    emit-value
                    v-model="block.additiveModel"
                    :label="blockKeys.additiveModel"
                    clearable
                    standout
                    dense
                ></q-select>
                <q-toggle
                    class="my-toggle"
                    v-model="block.show"
                    @update:model-value="bus.emit('filterPointData')"
                    label="Show"
                    standout
                    dense
                ></q-toggle>
                <q-btn v-if="model.ownModel" flat icon="fas fa-trash-alt" @click="removeBlock(index)">
                    <q-tooltip>
                        Remove Block
                    </q-tooltip>
                </q-btn>
            </div>
            <q-separator></q-separator>
        </q-list>
        
        <q-btn v-if="model.ownModel" flat icon="fas fa-plus" @click="addBlock">
            <q-tooltip>
                Add Block
            </q-tooltip>
        </q-btn>
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
        methods: {
        },
    })
</script>

<style>
</style>
