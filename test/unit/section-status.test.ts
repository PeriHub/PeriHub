// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import { sectionStatus } from '../../src/lib/utils/schemaValidation';

const THERMAL = { name: 'T1', thermalModel: ['Thermal Flow'], thermalType: 'Bond based' };

describe('sectionStatus', () => {
  it('marks empty optional sections unused, empty required sections incomplete', () => {
    expect(sectionStatus('thermal', 'ThermalModel', 'array', [])).toBe('unused');
    expect(sectionStatus('damages', 'Damage', 'array', undefined)).toBe('unused');
    expect(sectionStatus('outputs', 'Output', 'array', [])).toBe('incomplete');
  });

  it('still checks entries of a used optional section', () => {
    expect(sectionStatus('thermal', 'ThermalModel', 'array', [THERMAL])).toBe('complete');
    expect(sectionStatus('thermal', 'ThermalModel', 'array', [{ name: 'T1' }])).toBe('incomplete');
  });

  it('honours isUsed for always-present object sections', () => {
    const contactUsed = (c: { contactModels?: unknown[] }) => !!c.contactModels?.length;
    expect(sectionStatus('contact', 'Contact', 'object', { contactModels: [] }, contactUsed)).toBe(
      'unused'
    );
    const deviationsUsed = (d: { enabled: boolean }) => d.enabled;
    expect(
      sectionStatus('deviations', 'Deviations', 'object', { enabled: false }, deviationsUsed)
    ).toBe('unused');
  });

  it('honours isReady, e.g. an uploaded-mesh model without a mesh', () => {
    const meshReady = (m: { meshSource?: string; meshFile?: string | null }) =>
      m.meshSource !== 'upload' || !!m.meshFile;
    const model = { modelFolderName: 'Default', twoDimensional: true, meshSource: 'upload' };
    expect(sectionStatus('model', 'Model', 'object', model, undefined, meshReady)).toBe(
      'incomplete'
    );
    expect(
      sectionStatus(
        'model',
        'Model',
        'object',
        { ...model, meshFile: 'm.txt' },
        undefined,
        meshReady
      )
    ).toBe('complete');
  });
});
