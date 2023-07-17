import { defineStore } from "pinia";
import { api, trameApi } from 'boot/axios'
import axios from "axios";

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
      this.darkMode = !this.darkMode;
    },
    initialiseStore() {
      if (process.env.VUE_APP_DEV) {
        console.log(`I'm on a development build`);
      }else{
        let reqOptions = {
          url: "https://perihub.fa-services.intra.dlr.de",
        };
        axios
          .request(reqOptions)
          .then(response => {
            api.defaults.headers.common['Authorization'] = response.headers.authorization
            trameApi.defaults.headers.common['Authorization'] = response.headers.authorization
            // console.log('login', {token: response.headers.authorization})
          })
      }
    },
  },
});
