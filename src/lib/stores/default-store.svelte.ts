// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { config } from '$lib/config';
import type { Status } from '$lib/client';

function browser() {
  return typeof window !== 'undefined';
}

class DefaultStore {
  username = $state('');
  cluster = $state('');
  gravatarUrl = $state('US');
  useGravatar = $state(false);
  darkMode = $state(false);
  saveEnergy = $state(true);
  dev = $state(false);
  trial = $state(false);
  status = $state<Status>({} as Status);

  initialiseStore() {
    this.dev = config.dev;
    this.trial = config.trial;

    if (!browser()) return;

    if (localStorage.getItem('darkMode') === 'true') {
      this.darkMode = true;
    }
    if (localStorage.getItem('saveEnergy')) {
      this.saveEnergy = localStorage.getItem('saveEnergy') === 'true';
    }
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    if (browser()) {
      localStorage.setItem('darkMode', String(this.darkMode));
      document.documentElement.classList.toggle('dark', this.darkMode);
    }
  }
}

export const defaultStore = new DefaultStore();
