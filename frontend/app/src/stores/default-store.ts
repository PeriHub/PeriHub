// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';

export const useDefaultStore = defineStore('default', {
  state: () => ({
    username: '',
    cluster: '',
    gravatarUrl: 'US',
    useGravatar: false,
    darkMode: false,
    saveEnergy: true,
    DEV: false,
    TRIAL: false,

    status: {
      created: false,
      submitted: false,
      results: false,
      meshfileExist: false,
    },
  }),
  actions: {
    initialiseStore() {
      this.DEV = process.env.DEV;
      this.TRIAL = process.env.TRIAL;
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    },
  },
});
