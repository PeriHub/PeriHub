<template>
    <q-page class="flex-center">
        <q-splitter v-model="verticalSplitterModel" class="body" :limits="[30, 60]">
            <template v-slot:before>
                <div class="q-pa-md">
                    <ModelActions/>
                    <ExpansionComp/>
                </div>
            </template>

            <template v-slot:after>
                <q-splitter v-model="horizontalSplitterModel" horizontal>
                    <template v-slot:before>
                        <q-resize-observer @resize="onResizeBefore" :debounce="0" />
                        <div class="q-pa-md">
                            <ViewActions/>
                            <ViewComp/>
                        </div>
                    </template>
                    <template v-slot:after>
                        <q-resize-observer @resize="onResizeAfter" :debounce="0" />
                        <div class="q-pa-md">
                            <TextActions/>
                            <TextComp/>
                        </div>
                    </template>
                </q-splitter>
            </template>
        </q-splitter>
    </q-page>
</template>

<script>
    import ModelActions from 'src/components/actions/ModelActions.vue'
    import ExpansionComp from 'src/components/ExpansionComp.vue'
    import ViewActions from 'src/components/actions/ViewActions.vue'
    import ViewComp from 'src/components/ViewComp.vue'
    import TextActions from 'src/components/actions/TextActions.vue'
    import TextComp from 'src/components/TextComp.vue'

    import { inject } from 'vue'

    export default {
        name: "PeriHub",
        components: {
            ModelActions,
            ExpansionComp,
            ViewActions,
            ViewComp,
            TextActions,
            TextComp
        },
        setup() {
            const bus = inject('bus')

            return {
                bus
            }
        },
        data() {
            return {
                verticalSplitterModel: 50,
                horizontalSplitterModel: 50,
            };
        },
        methods: {
            onResizeBefore ({ width, height }) {
                // console.log("get resize", width, height)
                this.bus.emit('resizeViewPanel', height)
            },
            onResizeAfter ({ width, height }) {
                // console.log("get resize", width, height)
                this.bus.emit('resizeTextPanel', height)
            }
        },
    };
</script>

<style>
.body {
  height: calc(100vh - 116px);
  flex: auto;
}
</style>