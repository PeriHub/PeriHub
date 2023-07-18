<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-layout view="hHh lpR fFf">

    <MainHeader/>

    <q-drawer
        side="left" 
        v-model="drawer"
        show-if-above

        :mini="miniState"
        @mouseover="miniState = false"
        @mouseout="miniState = true"

        :width="300"
        :breakpoint="500"
        bordered
        class="bg-grey-3">
      <GuideDrawer></GuideDrawer>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <MainFooter/>

  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue';
import { useDefaultStore } from 'stores/default-store';
import MainHeader from 'layouts/MainHeader.vue'
import MainFooter from 'layouts/MainFooter.vue'
import GuideDrawer from 'components/GuideDrawer.vue'

export default defineComponent({
  name: 'MainLayout',
  components: {
    MainHeader,
    MainFooter,
    GuideDrawer
  },
  setup() {
    const store = useDefaultStore();
    return {
      store,
      drawer: ref(false),
      miniState: ref(true)
    }
  },
  methods: {
    initializeDarkMode() {
      this.$q.dark.set(localStorage.getItem("darkMode") == "true");
    },
  },
  async beforeMount() {
    await this.store.initialiseStore();
    if (localStorage.getItem("darkMode") == "true") {
      this.store.darkMode = true;
      this.$q.dark.toggle();
    }
  },

})
</script>
<style scoped>
.img{
  width:100%
}
</style>
