import { describe, expect, it } from 'vitest';
import { parseResultsFrame } from '../../src/lib/utils/results-frame';

// Mirrors encode_frame in backend/app/routers/results.py.
function encode(points: number[], values: number[], header: object): ArrayBuffer {
  let head = JSON.stringify({ ...header, count: values.length });
  head += ' '.repeat((4 - (head.length % 4)) % 4);
  const bytes = new TextEncoder().encode(head);
  const buffer = new ArrayBuffer(4 + bytes.length + 4 * (points.length + values.length));
  new DataView(buffer).setUint32(0, bytes.length, true);
  new Uint8Array(buffer, 4).set(bytes);
  new Float32Array(buffer, 4 + bytes.length).set([...points, ...values]);
  return buffer;
}

describe('parseResultsFrame', () => {
  it('reads header and float arrays', () => {
    const frame = parseResultsFrame(
      encode([0, 1, 2, 3, 4, 5], [0.5, -1], {
        variables: ['Damage'],
        number_of_steps: 7,
        min_value: -1,
        max_value: 0.5,
        time: 0.25
      })
    );
    expect(Array.from(frame.points)).toEqual([0, 1, 2, 3, 4, 5]);
    expect(Array.from(frame.values)).toEqual([0.5, -1]);
    expect(frame.variables).toEqual(['Damage']);
    expect(frame.numberOfSteps).toBe(7);
    expect(frame.time).toBe(0.25);
  });
});
