<template>
    <q-page class="flex-center">
        <q-splitter v-model="verticalSplitterModel" style="height:100%">
            <template v-slot:before>
                <div class="q-pa-md">
                    <ModelActions/>
                    <ExpansionComp/>
                </div>
            </template>

            <template v-slot:after>
                <q-splitter v-model="horizontalSplitterModel" horizontal>
                    <template v-slot:before>
                        <div class="q-pa-md" style="height:100%;width:100%">
                            <ViewActions/>
                            <ViewComp/>
                        </div>
                    </template>
                    <template v-slot:after>
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