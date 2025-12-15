// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';
import type { Status } from 'src/client';

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

    status: {} as Status,
  }),
  actions: {
    initialiseStore() {
      this.DEV = String(process.env.DEV).toLowerCase() === 'true';
      console.log(this.DEV);
      this.TRIAL = String(process.env.TRIAL).toLowerCase() === 'true';
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    },
  },
});
