/** One time step of a run as sent by `GET /results/points` (see `encode_frame` in backend/app/routers/results.py). */
export interface ResultsFrame {
  /** Flat xyz per point. */
  points: Float32Array;
  /** One value per point. */
  values: Float32Array;
  variables: string[];
  numberOfSteps: number;
  minValue: number;
  maxValue: number;
  time: number;
}

/**
 * Binary frame: uint32 LE header length, JSON header (padded to a multiple of 4), float32 LE points then values.
 * The arrays are views on the buffer - no copy, no per-number parsing.
 */
export function parseResultsFrame(buffer: ArrayBuffer): ResultsFrame {
  const headerLength = new DataView(buffer).getUint32(0, true);
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 4, headerLength)));
  const offset = 4 + headerLength;
  const count: number = header.count;
  return {
    points: new Float32Array(buffer, offset, 3 * count),
    values: new Float32Array(buffer, offset + 12 * count, count),
    variables: header.variables,
    numberOfSteps: header.number_of_steps,
    minValue: header.min_value,
    maxValue: header.max_value,
    time: header.time
  };
}
