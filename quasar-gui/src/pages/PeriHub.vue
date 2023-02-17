<template>
    <q-page class="flex-center">
        <q-splitter v-model="verticalSplitterModel" style="height:500px">
            <template v-slot:before>
                <div class="q-pa-md">
                    <ModelActions/>
                    <ExpansionComp/>
                </div>
            </template>

            <template v-slot:after>
                <q-splitter v-model="horizontalSplitterModel" horizontal>
                    <template v-slot:before>
                        <div class="q-pa-md" style="height:100%">
                            <ViewComp/>
                        </div>
                    </template>
                    <template v-slot:after>
                        <div class="q-pa-md">
                            <ViewComp/>
                        </div>
                    </template>
                </q-splitter>
            </template>
        </q-splitter>
    </q-page>
</template>

<script>
    import ModelActions from 'src/components/ModelActions.vue'
    import ExpansionComp from 'src/components/ExpansionComp.vue'
    import ViewComp from 'src/components/ViewComp.vue'
    export default {
    name: "PeriHub",
    components: {
        ModelActions,
        ExpansionComp,
        ViewComp
    },
    data() {
        return {
            verticalSplitterModel: 50,
            horizontalSplitterModel: 50,
        };
    },
    methods: {},
    };
</script>

<style>
</style>