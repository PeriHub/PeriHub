// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';

export const useDefaultStore = defineStore('default', {
  state: () => ({
    username: '',
    cluster: '',
    gravatarUrl: '',
    useGravatar: false,
    darkMode: false,
    saveEnergy: true,

    status: {
      created: false,
      submitted: false,
      results: false,
      meshfileExist: false,
    },
  }),
  actions: {
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    },
  },
});
