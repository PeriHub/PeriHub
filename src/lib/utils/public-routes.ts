/** Routes anonymous visitors may see; everything else needs a login (UX only - the backend enforces it). */
const PUBLIC = [
  '/',
  '/auth',
  '/models',
  '/materials',
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
