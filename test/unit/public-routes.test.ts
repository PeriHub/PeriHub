// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import { isPublicPath } from '../../src/lib/utils/public-routes';

describe('isPublicPath', () => {
  it.each([
    '/',
    '/auth/login',
    '/auth/callback',
    '/models',
    '/publications',
    '/tools',
    '/impressum'
  ])('allows %s', (path) => expect(isPublicPath(path)).toBe(true));

  it.each(['/perihub', '/admin', '/modelsx', '/authx'])('protects %s', (path) =>
    expect(isPublicPath(path)).toBe(false)
  );
});
