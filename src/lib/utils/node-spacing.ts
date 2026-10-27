/**
 * Node spacing of a point cloud (flat xyz array) for the sphere size of the 3D views: the median nearest-neighbour
 * distance of up to `samples` evenly spread nodes. Independent of node order, unlike the distance between the
 * first two nodes. ponytail: O(samples * n) brute force, fine for the views' node cap; use a grid if n grows a lot.
 */
export function nodeSpacing(points: ArrayLike<number>, samples = 100): number {
  const n = Math.floor(points.length / 3);
  if (n < 2) return 1;
  const step = Math.max(1, Math.floor(n / samples));
  const nearest: number[] = [];
  for (let i = 0; i < n; i += step) {
    let best = Infinity;
    for (let j = 0; j < n; j++) {
      if (j === i) continue;
      const d =
        (points[3 * i]! - points[3 * j]!) ** 2 +
        (points[3 * i + 1]! - points[3 * j + 1]!) ** 2 +
        (points[3 * i + 2]! - points[3 * j + 2]!) ** 2;
      // Duplicate nodes (d = 0) say nothing about the spacing.
      if (d > 0 && d < best) best = d;
    }
    if (best < Infinity) nearest.push(Math.sqrt(best));
  }
  if (!nearest.length) return 1;
  nearest.sort((a, b) => a - b);
  return nearest[Math.floor(nearest.length / 2)]!;
}
