// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';
import type { ModelData, Valves, GetModelsResponse } from 'src/client';
import { $ModelData } from 'src/client';

export const useModelStore = defineStore('model', {
  state: () => ({
    // @ts-expect-error Bla
    modelData: { ...$ModelData.example } as ModelData,
    availableModels: [] as GetModelsResponse,
    modelParams: {} as Valves,
    selectedModel: {
      title: 'Compact Tenison',
      file: 'CompactTension',
    },
  }),
  actions: {
    initialiseStore() {
      if (localStorage.getItem('modelData')) {
        console.log('initialiseStore');
        const object = JSON.parse(localStorage.getItem('modelData')!);
        this.modelData = structuredClone(object);
      }
      if (localStorage.getItem('selectedModel')) {
        const object = JSON.parse(localStorage.getItem('selectedModel')!);
        this.selectedModel = structuredClone(object);
      }
      if (localStorage.getItem('modelParams')) {
        const object = JSON.parse(localStorage.getItem('modelParams')!);
        this.modelParams = structuredClone(object);
      }
    },
  },
});
