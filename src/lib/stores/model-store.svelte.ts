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
  // Which model's config/valves are currently loaded into modelData /
  // modelParams (null until a real fetch happens - the schema `example`
  // defaults above never set these). Compared against selectedModel.file
  // by utils/modelSync.ts to tell a genuinely stale/mismatched cache apart
  // from one that's already correct for the selected model, so a page
  // reload can auto-refresh only when it actually needs to, without
  // clobbering in-progress edits on every load.
  modelDataFile = $state<string | null>(null);
  modelParamsFile = $state<string | null>(null);

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
    const modelDataFile = localStorage.getItem('modelDataFile');
    if (modelDataFile) {
      this.modelDataFile = modelDataFile;
    }
    const modelParamsFile = localStorage.getItem('modelParamsFile');
    if (modelParamsFile) {
      this.modelParamsFile = modelParamsFile;
    }
  }
}

export const modelStore = new ModelStore();

// Restore any cached values BEFORE the persistence effects below are set up.
// Those effects run once immediately on creation (with modelData/modelParams
// still at their default $state values), so without this, that first run
// would overwrite the just-cached localStorage entries with the defaults
// before initialiseStore() (called later, from +layout.svelte's onMount)
// ever gets a chance to read them back.
modelStore.initialiseStore();

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
    $effect(() => {
      if (modelStore.modelDataFile) {
        localStorage.setItem('modelDataFile', modelStore.modelDataFile);
      }
    });
    $effect(() => {
      if (modelStore.modelParamsFile) {
        localStorage.setItem('modelParamsFile', modelStore.modelParamsFile);
      }
    });
  });
}
