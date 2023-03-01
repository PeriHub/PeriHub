<template>
  <q-layout view="hHh lpR fFf">

    <MainHeader/>

    <q-page-container>
      <router-view />
    </q-page-container>

    <MainFooter/>

  </q-layout>
</template>

<script>
import { defineComponent } from 'vue';
import { useDefaultStore } from 'stores/default-store';
import MainHeader from 'layouts/MainHeader.vue'
import MainFooter from 'layouts/MainFooter.vue'

export default defineComponent({
  name: 'MainLayout',
  data() {
    return {
    }
  },
  components: {
    MainHeader,
    MainFooter,
  },
  setup() {
    const store = useDefaultStore();
    return {
      store,
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
