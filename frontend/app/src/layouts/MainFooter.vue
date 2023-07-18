<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <q-footer elevated color="primary">
      <q-toolbar>
        <div style="text-align: center; width:100%">
          <div>
            <q-btn flat text-color="white" label="ABOUT US" href="https://www.dlr.de/fa"></q-btn>
            <q-btn flat text-color="white" label="BLOG" href="https://leichtbau.dlr.de/"></q-btn>
            <q-btn flat text-color="white" label="CONTACT US" href="mailto:Jan-Timo.Hesse@dlr.de"></q-btn>
          </div>
          <div>
            {{ new Date().getFullYear() }} — <strong>PeriHub</strong> | Jan-Timo
            Hesse | Christian Willberg | Falk Heinecke
          </div>
        </div>
      </q-toolbar>
    </q-footer>
</template>

<script>
import { defineComponent } from 'vue'
import { useDefaultStore } from 'stores/default-store';
export default defineComponent({
    name: "MainFooter",
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
<style></style>
