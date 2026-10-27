/**
 * True if `data` is already in the current schema-driven shape, where every PeriLab key lives in an
 * entry's `params` dict - rather than an older, pre-`params` config (no backward compatibility: those must
 * fail loudly instead of loading with values silently missing).
 *
 * Accepts either a full ModelData-like object (checks every `blocks[]` entry has `params`, and every
 * `solvers[]` entry too, if present) or a single Entry-like object such as a library material (current-shape
 * if it has `params` itself).
 */
export function isCurrentShape(data: unknown): boolean {
  if (!data || typeof data !== 'object') return false;
  const obj = data as Record<string, unknown>;
  if (Array.isArray(obj.blocks)) {
    const hasParams = (entry: unknown) => !!(entry as { params?: unknown } | null)?.params;
    const blocksOk = obj.blocks.every(hasParams);
    const solversOk = !Array.isArray(obj.solvers) || obj.solvers.every(hasParams);
    return blocksOk && solversOk;
  }
  return !!obj.params;
}
