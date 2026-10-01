// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/** Routes anonymous visitors may see; everything else needs a login (UX only - the backend enforces it). */
const PUBLIC = [
  '/',
  '/auth',
  '/models',
  '/publications',
  '/tools',
  '/impressum',
  '/privacy',
  '/copyright',
  '/accessibility'
];

export function isPublicPath(path: string): boolean {
  return PUBLIC.some((p) => path === p || (p !== '/' && path.startsWith(p + '/')));
}
