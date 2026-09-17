// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import type { ModelData, Valves, GetModelsResponse } from '$lib/client';
import { $ModelData as ModelDataSchema, $Valves as ValvesSchema } from '$lib/client';

function browser() {
  return typeof window !== 'undefined';
}

class ModelStore {
  // @ts-expect-error the generated schema's `example` is typed loosely
  modelData = $state<ModelData>({ ...ModelDataSchema.example });
  availableModels = $state<GetModelsResponse>([]);
  // @ts-expect-error the generated schema's `example` is typed loosely
  modelParams = $state<Valves>({ ...ValvesSchema.example });
  selectedModel = $state({
    title: 'Compact Tenison',
    file: 'CompactTension'
  });

  initialiseStore() {
    if (!browser()) return;

    const modelData = localStorage.getItem('modelData');
    if (modelData) {
      this.modelData = structuredClone(JSON.parse(modelData));
    }
    const selectedModel = localStorage.getItem('selectedModel');
    if (selectedModel) {
      this.selectedModel = structuredClone(JSON.parse(selectedModel));
    }
    const modelParams = localStorage.getItem('modelParams');
    if (modelParams) {
      this.modelParams = structuredClone(JSON.parse(modelParams));
    }
  }
}

export const modelStore = new ModelStore();

// Persist to localStorage whenever modelData/modelParams change, mirroring
// the deep watchers in the old MainLayout.vue.
if (browser()) {
  $effect.root(() => {
    $effect(() => {
      localStorage.setItem('modelData', JSON.stringify(modelStore.modelData));
    });
    $effect(() => {
      localStorage.setItem('modelParams', JSON.stringify(modelStore.modelParams));
    });
  });
}
