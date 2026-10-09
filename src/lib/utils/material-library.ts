// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import type { LibraryItemIn, LibraryItemOut, Material } from '$lib/client';

/** A library entry stores one model material (minus its position/link in a model) as `properties`. */
export function toLibraryProperties(material: Material): Record<string, unknown> {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { materialsId, libraryId, ...rest } = material;
  return rest;
}

/** Copy a library material into a model slot: keeps the slot's materialsId and remembers the source.
 *  Pass a plain object (`$state.snapshot`) - structuredClone throws on $state proxies. */
export function fromLibrary(
  item: LibraryItemOut,
  materialsId: number | null | undefined
): Material {
  return {
    ...structuredClone(item.properties ?? {}),
    name: item.name,
    materialsId,
    libraryId: item.id
  } as Material;
}

/** PUT body that replaces the content but keeps the item's sharing settings. */
export function libraryUpdateBody(item: LibraryItemOut, material: Material): LibraryItemIn {
  return {
    name: material.name,
    visibility: item.visibility as LibraryItemIn['visibility'],
    team_id: item.team_id,
    project_id: item.project_id,
    tags: item.tags,
    source: item.source,
    properties: toLibraryProperties(material)
  };
}

export function newMaterial(): Material {
  return {
    name: 'New material',
    matType: ['PD Solid Elastic'],
    materialSymmetry: 'Isotropic',
    stabilizationType: 'Global Stiffness',
    hourglassCoefficient: 1,
    planeStress: true,
    planeStrain: false,
    poissonsRatio: null,
    youngsModulus: null,
    properties: null
  };
}

export const VISIBILITY_LABELS: Record<string, string> = {
  private: 'Private',
  team: 'Team',
  org: 'Organization',
  public: 'Public'
};
