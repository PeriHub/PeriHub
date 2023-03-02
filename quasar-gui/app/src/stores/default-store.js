import { defineStore } from "pinia";
import { api } from 'boot/axios'
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
      if (process.env.DEV) {
        console.log(`I'm on a development build`);
      }else{
        let reqOptions = {
          url: "https://perihub.fa-services.intra.dlr.de",
        };
        axios
          .request(reqOptions)
          .then(response => {
            api.defaults.headers.common['Authorization'] = 'Bearer ' + response.headers.authorization
            commit('login', {token: response.headers.authorization})
          })
      }
    },
  },
});
