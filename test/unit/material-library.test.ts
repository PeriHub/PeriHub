import { describe, expect, it } from 'vitest';
import type { LibraryItemOut } from '../../src/lib/client';
import {
  fromLibrary,
  libraryUpdateBody,
  newMaterial,
  toLibraryProperties
} from '../../src/lib/utils/material-library';

const item: LibraryItemOut = {
  id: 'lib-1',
  owner_id: 'u1',
  org_id: 'o1',
  team_id: 't1',
  project_id: null,
  name: 'Steel',
  visibility: 'team',
  tags: ['metal'],
  properties: {
    ...newMaterial(),
    name: 'old name',
    params: { ...newMaterial().params, "Young's Modulus": 210000 }
  }
};

describe('material library mapping', () => {
  it('strips the model slot and link when storing', () => {
    const props = toLibraryProperties({ ...newMaterial(), materialsId: 3, libraryId: 'x' });
    expect(props).not.toHaveProperty('materialsId');
    expect(props).not.toHaveProperty('libraryId');
  });

  it('loads into a slot: keeps materialsId, links the source, takes the item name', () => {
    const m = fromLibrary(item, 2);
    expect(m).toMatchObject({
      materialsId: 2,
      libraryId: 'lib-1',
      name: 'Steel',
      params: { "Young's Modulus": 210000 }
    });
    m!.params!["Young's Modulus"] = 1;
    expect((item.properties as { params: Record<string, number> }).params["Young's Modulus"]).toBe(
      210000
    );
  });

  it('returns null for a material saved before PeriLab keys moved into params', () => {
    const old: LibraryItemOut = {
      ...item,
      properties: { name: 'old name', youngsModulus: 210000 }
    };
    expect(fromLibrary(old, 2)).toBeNull();
  });

  it('overwrite keeps the sharing settings', () => {
    const body = libraryUpdateBody(item, { ...newMaterial(), name: 'Steel 2', materialsId: 1 });
    expect(body).toMatchObject({
      name: 'Steel 2',
      visibility: 'team',
      team_id: 't1',
      tags: ['metal']
    });
    expect(body.properties).not.toHaveProperty('materialsId');
  });

  it('creates new materials in the params shape', () => {
    expect(newMaterial()).toEqual({
      name: 'New material',
      params: {
        'Material Model': 'PD Solid Elastic',
        Symmetry: 'isotropic plane stress',
        'Zero Energy Control': 'Global'
      },
      properties: []
    });
  });
});
