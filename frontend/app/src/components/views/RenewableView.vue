<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <area-chart :data=plot_data label="Percent of renewable energy share"></area-chart>
</template>

<script>
import { defineComponent } from 'vue'
import { inject } from 'vue'
import { useViewStore } from 'stores/view-store';
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

    this.$api.get('/energy/prognosis')
      .then((response) => {
        this.$q.notify({
          message: response.data.message
        })
        this.plot_data = response.data.data;
      })
      .catch((error) => {
        this.$q.notify({
          color: 'negative',
          position: 'bottom-right',
          message: response.data.message,
          icon: 'report_problem'
        })
      })

  }
})
</script>

<style></style>
