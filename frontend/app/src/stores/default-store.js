// SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from "pinia";
// import { api, trameApi } from "boot/axios";
import { api } from "boot/axios";
import axios from "axios";

export const useDefaultStore = defineStore("default", {
  state: () => ({
    darkMode: false,
    saveEnergy: true,

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
      if (process.env.TRIAL) {
        console.log(`I'm on a trial build`);
        if (localStorage.getItem("userName") != null) {
          api.defaults.headers.common["userName"] =
            localStorage.getItem("userName");
        } else {
          let reqOptions = {
            url: "https://randomuser.me/api",
          };
          axios.request(reqOptions).then((response) => {
            const uuid = response.data.results[0].login.uuid;
            console.log(uuid);
            api.defaults.headers.common["userName"] = uuid;
            localStorage.setItem("userName", uuid);
          });
        }
      }
      if (process.env.DEV) {
        console.log(`I'm on a development build`);
      } else {
        let reqOptions = {
          url: "https://perihub.fa-services.intra.dlr.de",
        };
        axios.request(reqOptions).then((response) => {
          api.defaults.headers.common["Authorization"] =
            response.headers.authorization;
          trameApi.defaults.headers.common["Authorization"] =
            response.headers.authorization;
          // console.log('login', {token: response.headers.authorization})
        });
      }
    },
  },
});
