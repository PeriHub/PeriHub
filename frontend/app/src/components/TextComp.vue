<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div :style="{'height': textHeight}">
        <q-tabs
            v-model="store.textId"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
        >
            <q-tab name="input" label="Input"></q-tab>
            <q-tab name="log" label="Log"></q-tab>
        </q-tabs>

        <q-separator></q-separator>

        <q-tab-panels v-model="store.textId" animated style="height:100%">
          <q-tab-panel name="input">
            <TextView></TextView>
          </q-tab-panel>
          <q-tab-panel name="log">
            <LogView></LogView>
          </q-tab-panel>
        </q-tab-panels>

        <q-inner-loading :showing="store.textLoading">
            <q-spinner-gears size="50px" color="primary"></q-spinner-gears>
        </q-inner-loading>
    </div>
</template>

<script>
import { defineComponent, inject } from 'vue'
import TextView from 'components/views/TextView.vue'
import LogView from 'components/views/LogView.vue'
import { useViewStore } from 'stores/view-store';

export default defineComponent({
    name: "TextComp",
    components: {
        TextView,
        LogView
    },
    data() {
        return {
            textHeight: "400px",
        };
    },
    setup() {
        const store = useViewStore();
        const bus = inject('bus');
        return {
            store,
            bus
        }
    },
    created() {
        this.bus.on('resizeTextPanel', (height) => {
            this.textHeight = height - 113 + 'px'
        })
    },
})
</script>