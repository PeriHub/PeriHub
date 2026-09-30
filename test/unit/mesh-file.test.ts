// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import { meshTypeFromFilename } from '../../src/lib/utils/mesh-file';

describe('meshTypeFromFilename', () => {
  it('detects mesh types by extension', () => {
    expect(meshTypeFromFilename('plate.txt')).toBe('txt');
    expect(meshTypeFromFilename('plate.e')).toBe('e');
    expect(meshTypeFromFilename('plate.G')).toBe('e');
    expect(meshTypeFromFilename('part.v2.GCODE')).toBe('gcode');
  });

  it('rejects everything else', () => {
    expect(meshTypeFromFilename('gcode')).toBeNull();
    expect(meshTypeFromFilename('mesh.g.ascii')).toBeNull();
    expect(meshTypeFromFilename('nodes.inp')).toBeNull();
  });
});
