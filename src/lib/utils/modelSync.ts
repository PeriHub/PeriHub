// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { getConfig, getValves } from '$lib/client';
import type { ModelData } from '$lib/client';
import { modelStore } from '$lib/stores/model-store.svelte';
import { notify } from './notify';

/**
 * Fetches `modelFile`'s config and valves from the backend and applies them
 * to modelStore, tagging modelDataFile/modelParamsFile so modelNeedsRefresh()
 * can tell them apart from a stale cache or one left over from a different
 * model. Used both for the explicit "Reset Data" action and for switching
 * the selected model, so both paths end up with the same, actually-correct
 * state instead of switching models only refreshing valves and silently
 * leaving the previous model's config in place until a manual reset.
 */
export function refreshModelFromBackend(modelFile: string) {
  getConfig({ configFile: modelFile })
    .then((response) => {
      const data = JSON.parse(JSON.stringify(response));
      modelStore.modelData = { ...modelStore.modelData, ...data } as ModelData;
      modelStore.modelDataFile = modelFile;
    })
    .catch((error) => notify.apiError(error));

  getValves({ modelName: modelFile })
    .then((response) => {
      modelStore.modelParams = structuredClone(response);
      modelStore.modelParamsFile = modelFile;
    })
    .catch((error) => notify.apiError(error));
}

/**
 * True when modelData/modelParams weren't fetched for `modelFile` yet - i.e.
 * this is the first visit ever (nothing cached), or localStorage's
 * selectedModel and modelData/modelParams have drifted apart between
 * sessions. False once they already match, so a page reload won't discard
 * in-progress edits by refetching on every mount.
 */
export function modelNeedsRefresh(modelFile: string) {
  return modelStore.modelDataFile !== modelFile || modelStore.modelParamsFile !== modelFile;
}
