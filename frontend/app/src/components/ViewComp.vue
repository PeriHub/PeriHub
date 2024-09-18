<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div :style="{ 'height': viewHeight }">
    <q-tabs v-model="viewStore.viewId" dense class="text-grey" active-color="primary" indicator-color="primary"
      align="justify">
      <q-tab name="image" label="Image"></q-tab>
      <q-tab name="model" label="Model"></q-tab>
      <q-tab name="cad" label="CAD"></q-tab>
      <q-tab name="jobs" label="Jobs"></q-tab>
      <q-tab name="results" label="Results"></q-tab>
      <q-tab name="plotly" label="Plotly"></q-tab>
      <q-tab v-show="store.saveEnergy" name="renewable" label="Renewable"></q-tab>
      <!-- <q-tab name="trame" label="Trame"></q-tab> -->
    </q-tabs>

    <q-separator></q-separator>

    <q-tab-panels v-model="viewStore.viewId" animated style="height:100%">
      <q-tab-panel name="image">
        <ImageView></ImageView>
      </q-tab-panel>

      <q-tab-panel name="model">
        <ModelView></ModelView>
      </q-tab-panel>

      <q-tab-panel name="cad">
        <CadView></CadView>
      </q-tab-panel>

      <q-tab-panel name="jobs">
        <JobsView></JobsView>
      </q-tab-panel>

      <q-tab-panel name="results">
        <ResultsView></ResultsView>
      </q-tab-panel>

      <q-tab-panel name="plotly">
        <PlotlyView></PlotlyView>
      </q-tab-panel>

      <q-tab-panel name="renewable">
        <RenewableView></RenewableView>
      </q-tab-panel>

      <!-- <q-tab-panel name="trame">
        <iframe :src="viewStore.resultPort" width="100%" height="100%" frameborder="0" />
      </q-tab-panel> -->

    </q-tab-panels>

    <q-inner-loading :showing="viewStore.modelLoading">
      <q-spinner-gears size="50px" color="primary"></q-spinner-gears>
    </q-inner-loading>
  </div>
</template>

<script>
import { inject, defineComponent } from 'vue'
import ImageView from 'components/views/ImageView.vue'
import ModelView from 'components/views/ModelView.vue'
import CadView from 'components/views/CadView.vue'
import JobsView from 'components/views/JobsView.vue'
import PlotlyView from 'components/views/PlotlyView.vue'
import RenewableView from 'components/views/RenewableView.vue'
import ResultsView from 'components/views/ResultsView.vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useViewStore } from 'src/stores/view-store';

export default defineComponent({
  name: 'ViewComp',
  components: {
    ImageView,
    ModelView,
    CadView,
    JobsView,
    PlotlyView,
    RenewableView,
    ResultsView
  },
  data() {
    return {
      viewHeight: '400px',
      tab: 'results',
    };
  },
  setup() {
    const store = useDefaultStore();
    const viewStore = useViewStore();
    const bus = inject('bus');
    return {
      store,
      viewStore,
      bus
    }
  },
  created() {
    this.bus.on('resizeViewPanel', (height) => {
      this.viewHeight = height - 89 + 'px'
    })
  },
})
</script>
<style>
.q-tab-panel {
  padding: 0px;
}
</style>
