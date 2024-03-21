// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
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
  },
});
