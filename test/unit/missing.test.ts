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
});
