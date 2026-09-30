// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export type MeshType = 'txt' | 'e' | 'gcode';

export const MESH_EXTENSIONS = '.txt,.e,.g,.gcode';

/** The discretization type of an uploaded mesh file (`discType`), or null if it isn't a mesh. */
export function meshTypeFromFilename(name: string): MeshType | null {
  const ext = name.toLowerCase().split('.').pop();
  if (!name.includes('.')) return null;
  if (ext === 'txt') return 'txt';
  if (ext === 'e' || ext === 'g') return 'e';
  if (ext === 'gcode') return 'gcode';
  return null;
}
