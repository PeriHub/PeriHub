<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <area-chart :data=plot_data label="Percent of renewable energy share"></area-chart>
</template>

<script>
import { defineComponent } from 'vue'
import { inject } from 'vue'
import { useViewStore } from 'src/stores/view-store';
import { getPrognosisEnergy } from 'src/client';
export default defineComponent({
  name: 'RenewableView',
  setup() {
    const viewStore = useViewStore();
    const bus = inject('bus')

    return {
      viewStore,
      bus
    }
  },
  data() {
    return {
      plot_data: {}
    };
  },
  methods: {},
  async mounted() {

    await getPrognosisEnergy()
      .then((response) => {
        this.$q.notify({
          message: response.message
        })
        this.plot_data = response.data;
      })
      .catch((error) => {
        this.$q.notify({
          color: 'negative',
          position: 'bottom-right',
          message: response.message,
          icon: 'report_problem'
        })
      })

  }
})
</script>

<style></style>
