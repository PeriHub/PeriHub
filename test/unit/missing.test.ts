import { describe, expect, it } from 'vitest';
import defaultModel from '../../backend/app/assets/default_model.json';
import type { ModelData } from '../../src/lib/client';
import { missingBySection } from '../../src/lib/perilab/missing';

const base = () => structuredClone(defaultModel) as unknown as ModelData;

describe('missingBySection', () => {
  it('reports nothing for the default model', () => {
    expect(Object.values(missingBySection(base())).flat()).toEqual([]);
  });

  it('names the entry and key of a missing required value', () => {
    const data = base();
    delete data.blocks[0]!.params!['Density'];
    expect(missingBySection(data).blocks).toEqual(['Part: Density']);
  });

  it('does not count Horizon for generated models, only for uploaded meshes', () => {
    const data = base();
    expect(missingBySection(data).blocks).toEqual([]);
    data.model.meshSource = 'upload';
    expect(missingBySection(data).blocks).toContain('Part: Horizon');
  });

  it('requires Thermal Conductivity for Thermal Flow only', () => {
    const data = base();
    data.thermal = [
      { name: 'T', params: { 'Thermal Model': 'Thermal Flow' } }
    ] as ModelData['thermal'];
    expect(missingBySection(data).thermal).toContain('T: Thermal Conductivity');
    data.thermal![0]!.params!['Thermal Model'] = 'Thermal Expansion';
    expect(missingBySection(data).thermal).not.toContain('T: Thermal Conductivity');
  });

  it('requires Specific Heat Capacity on every block once a block uses a thermal model', () => {
    const data = base();
    expect(missingBySection(data).blocks).toEqual([]);
    data.blocks[0]!.params!['Thermal Model'] = 'T';
    expect(missingBySection(data).blocks).toEqual(
      data.blocks.map((b) => `${b.name}: Specific Heat Capacity`)
    );
  });
});
