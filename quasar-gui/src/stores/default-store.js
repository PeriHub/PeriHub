import { defineStore } from "pinia";

export const useDefaultStore = defineStore("default", {
  state: () => ({
    url: "https://perihub-api.fa-services.intra.dlr.de/",
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
        this.url = "http://localhost:6020/";
      }
      if (localStorage.getItem("darkMode") == "true") {
        this.darkMode = true;
      }
    },
  },
});
