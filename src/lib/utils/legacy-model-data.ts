// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import type { ModelData } from '$lib/client';

type LegacySection = { enabled?: boolean; [key: string]: unknown };

/**
 * Older configs (localStorage, saved runs, own-model JSON files) stored
 * `thermal`/`additive` as `{ enabled, thermalModels/additiveModels }` and
 * `contact` with an `enabled` flag. Sections are now plain arrays (empty =
 * off), so convert on load; a disabled legacy section maps to `[]`.
 * `model.ownModel` (= uploaded mesh) became `model.meshSource`; `ownMesh` was unused.
 * Mirrors the validators in backend/app/support/base_models.py.
 */
export function normalizeModelData<T extends Partial<ModelData>>(data: T): T {
  for (const key of ['thermal', 'additive'] as const) {
    const value = data[key] as unknown;
    if (value && !Array.isArray(value)) {
      const legacy = value as LegacySection;
      (data as Record<string, unknown>)[key] = legacy.enabled ? (legacy[`${key}Models`] ?? []) : [];
    }
  }
  const contact = data.contact as LegacySection | null | undefined;
  if (contact && 'enabled' in contact) {
    const { enabled, ...rest } = contact;
    data.contact = (
      enabled === false ? { ...rest, contactModels: [] } : rest
    ) as ModelData['contact'];
  }
  const model = data.model as (Record<string, unknown> & { meshSource?: string }) | undefined;
  if (model && ('ownModel' in model || 'ownMesh' in model)) {
    model.meshSource ??= model.ownModel ? 'upload' : 'model';
    delete model.ownModel;
    delete model.ownMesh;
  }
  return data;
}
