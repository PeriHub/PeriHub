<template>
    <q-list bordered class="rounded-borders">
        <q-expansion-item
            expand-separator
            icon="fas fa-th"
            label="Blocks"
            caption="John Doe"
        >
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
                        outlined
                        dense
                    ></q-input>
                    <q-select 
                        class="my-input"
                        :options="materials"
                        v-model="block.material"
                        :label="blockKeys.material"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="damages"
                        v-model="block.damageModel"
                        :label="blockKeys.damageModel"
                        clearable
                        outlined
                        dense
                    ></q-select>
                    <q-toggle
                        class="my-toggle"
                        v-model="block.show"
                        @change="bus.emit('filterPointData')"
                        label="Show"
                        outlined
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
        </q-expansion-item>
    </q-list>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
    import { deepCopy } from '../../utils/functions.js'
  
    export default defineComponent({
        name: 'BlocksSettings',
        setup() {
            const store = useModelStore();
            const model = computed(() => store.modelData.model)
            const materials = computed(() => store.modelData.materials)
            const damages = computed(() => store.modelData.damages)
            const blocks = computed(() => store.modelData.blocks)
            const bus = inject('bus')
            return {
                store,
                model,
                materials,
                damages,
                blocks,
                rules,
                bus
            }
        },
        created() {
        },
        data() {
            return {
                blockKeys: {
                    name: "Block Names",
                    material: "Material",
                    damageModel: "Damage Model",
                    horizon: "Horizon",
                },
            };
        },
        methods: {
            addBlock() {
                const len = this.blocks.length;
                let newItem = deepCopy(this.blocks[len - 1])
                newItem.blocksId = len + 1
                newItem.name = "block_" + (len + 1)
                this.blocks.push(newItem);
            },
            removeBlock(index) {
                this.blocks.splice(index, 1);
            },
        }
    })
</script>
<style>
.my-title {
    margin-top: 10px;
    margin-bottom: 0px;
    margin-left: 10px;
}
.my-row {
    min-height: 50px;
}
.my-input {
    margin-left: 10px;
}
.my-toggle {
    height: 40px;
    margin: 10px;
}
</style>