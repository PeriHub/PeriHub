// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import type { ModelData } from '../../src/lib/client';
import { normalizeModelData } from '../../src/lib/utils/legacy-model-data';

describe('normalizeModelData', () => {
  it('unwraps legacy sections, dropping disabled ones', () => {
    const data = normalizeModelData({
      thermal: { enabled: false, thermalModels: [{ name: 'T1' }] },
      additive: { enabled: true, additiveModels: [{ name: 'A1' }] },
      contact: { enabled: false, contactModels: [{ name: 'C1' }], searchFrequency: 5 }
    } as unknown as ModelData);
    expect(data.thermal).toEqual([]);
    expect(data.additive).toEqual([{ name: 'A1' }]);
    expect(data.contact).toEqual({ contactModels: [], searchFrequency: 5 });
  });

  it('leaves the current format untouched', () => {
    const data = { thermal: [{ name: 'T1' }], additive: [], contact: { contactModels: [] } };
    expect(normalizeModelData(structuredClone(data) as unknown as ModelData)).toEqual(data);
  });

  it('maps the legacy ownModel flag to meshSource', () => {
    const own = normalizeModelData({
      model: { modelFolderName: 'D', twoDimensional: true, ownModel: true, ownMesh: null }
    } as unknown as ModelData);
    expect(own.model).toEqual({ modelFolderName: 'D', twoDimensional: true, meshSource: 'upload' });
    const predefined = normalizeModelData({ model: { ownModel: false } } as unknown as ModelData);
    expect(predefined.model).toEqual({ meshSource: 'model' });
  });
});
