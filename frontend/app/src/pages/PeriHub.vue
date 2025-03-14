<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="flex-center">
    <q-splitter v-model="verticalSplitterModel" class="body" :limits="[30, 60]">
      <template v-slot:before>
        <div class="q-pa-md">
          <ModelActions id="ModelActions" />
          <ExpansionComp id="ExpansionComp" />
        </div>
      </template>

      <template v-slot:after>
        <q-splitter v-model="horizontalSplitterModel" horizontal :limits="[1, 99]">
          <template v-slot:before>
            <q-resize-observer @resize="onResizeBefore" :debounce="0" />
            <div class="q-pa-md">
              <ViewActions id="ViewActions" />
              <ViewComp id="ViewComp" />
            </div>
          </template>
          <template v-slot:after>
            <q-resize-observer @resize="onResizeAfter" :debounce="0" />
            <div class="q-pa-md">
              <TextActions id="TextActions" />
              <TextComp id="TextComp" />
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
import { useDefaultStore } from 'src/stores/default-store';
import Driver from 'driver.js';
import 'driver.js/dist/driver.min.css';

import { inject } from 'vue'

export default {
  name: 'PeriHub',
  components: {
    ModelActions,
    ExpansionComp,
    ViewActions,
    ViewComp,
    TextActions,
    TextComp
  },
  setup() {
    const store = useDefaultStore();
    const bus = inject('bus')

    return {
      store,
      bus
    }
  },
  created() {
    this.bus.on('showTutorial', () => {
      this.showTutorial()
    })
  },
  data() {
    return {
      verticalSplitterModel: 40,
      horizontalSplitterModel: 50,
    };
  },
  methods: {
    onResizeBefore({ width, height }) {
      // console.log('get resize', width, height)
      this.bus.emit('resizeViewPanel', height)
    },
    onResizeAfter({ width, height }) {
      // console.log('get resize', width, height)
      this.bus.emit('resizeTextPanel', height)
    },
    showTutorial() {
      var color = 'white';
      if (this.store.darkMode) {
        color = 'gray';
      }

      const driver = new Driver({
        animate: true, // Animate while changing highlighted element
        opacity: 0.5,
        stageBackground: color,
      });

      // Define the steps for introduction
      driver.defineSteps([
        {
          element: '#ModelActions',
          popover: {
            className: 'first-step-popover-class',
            title: 'ModelActions',
            description: 'Here you are able to upload, save, switch and generate models',
            position: 'right',
          },
        },
        {
          element: '#ExpansionComp',
          popover: {
            title: 'ExpansionComp',
            description: 'Here you can find the configuration for your simulation',
            position: 'right',
          },
        },
        {
          element: '#ViewActions',
          popover: {
            title: 'ViewActions',
            description: 'Here you are able to submit your simulation, view your results and download them',
            position: 'left',
          },
        },
        {
          element: '#ViewComp',
          popover: {
            title: 'ViewComp',
            description: 'This is where your simulation results are displayed',
            position: 'left',
          },
        },
        {
          element: '#TextActions',
          popover: {
            title: 'TextActions',
            description: 'If you want to edit your input-deck you can save it here',
            position: 'left',
          },
        },
        {
          element: '#TextComp',
          popover: {
            title: 'TextComp',
            description: 'This is where your input-deck or log-file is displayed',
            position: 'left',
          },
        },
      ]);

      // Start the introduction
      driver.start();
    },
  },
};
</script>

<style>
.body {
  height: calc(100vh - 117px);
  flex: auto;
}
</style>
