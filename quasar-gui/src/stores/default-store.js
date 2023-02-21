import { defineStore } from "pinia";

export const useDefaultStore = defineStore("default", {
  state: () => ({
    darkMode: false,

    status: {
      created: false,
      submitted: false,
      results: false,
    },
  }),
  actions: {
    toggleDarkMode() {
      localStorage.setItem("darkMode", !this.darkMode);
      this.darkMode = !this.darkMode;
    },
    initialiseStore() {
      if (process.env.DEV) {
        console.log(`I'm on a development build`);
      }
      if (localStorage.getItem("darkMode") == "true") {
        this.darkMode = true;
      }
    },
  },
});
