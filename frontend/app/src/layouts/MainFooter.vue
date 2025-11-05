<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-footer elevated color="primary" reveal>
    <q-toolbar>
      <div style="text-align: center; width:100%">
        <div :style="{ fontSize: $q.screen.lt.md ? '10px' : '12px' }">
          <q-btn :style="buttonStyle" flat text-color="white" label="ABOUT US" href="https://www.dlr.de/sy"></q-btn>
          <q-btn :style="buttonStyle" flat text-color="white" label="BLOG" href="https://leichtbau.dlr.de/"></q-btn>
          <q-btn :style="buttonStyle" flat text-color="white" label="CONTACT US"
            href="mailto:Jan-Timo.Hesse@dlr.de"></q-btn> --
          <q-btn :style="buttonStyle" flat text-color="white" label="IMPRESSUM" to="/impressum"></q-btn>
          <q-btn :style="buttonStyle" flat text-color="white" label="PRIVACY POLICY" to="/privacy"></q-btn>
          <q-btn :style="buttonStyle" flat text-color="white" label="TERMS OF USE" to="/copyright"></q-btn>
          <q-btn :style="buttonStyle" flat text-color="white" label="ACCESSIBILITY STATEMENT"
            to="/accessibility"></q-btn>
        </div>
        <div :style="{ fontSize: $q.screen.lt.md ? '12' : '14' }">
          © {{ new Date().getFullYear() }} German Aerospace Center (DLR) — <strong>PeriHub</strong> | Jan-Timo
          Hesse | Christian Willberg
        </div>
      </div>
    </q-toolbar>
  </q-footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
export default defineComponent({
  name: "MainFooter",
  computed: {
    buttonStyle() {
      return {
        fontSize: this.$q.screen.lt.md ? '10px' : '12px'
      };
    }
  },
  setup() {
    const store = useDefaultStore();
    return {
      store,
    }
  },
  data() {
    return {
    };
  },
})
</script>
<style>
.q-btn {
  margin-right: 5px;
  margin-left: 5px;
  padding: 0px;
}
</style>
