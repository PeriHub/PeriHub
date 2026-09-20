// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export interface LogProgress {
  percent: number;
  currentStep: number;
  totalSteps: number;
}

// Mirrors backend/app/support/file_handler.py's FileHandler.parse_progress -
// looks for the most recent `[Info] Step: <current> / <total>` line, one of
// which PeriLab prints per output time step. Used to show a live progress
// bar from the log text already streamed over the websocket, with zero
// extra round-trips. Returns null if no such line is present yet (e.g. a
// PeriLab build that doesn't emit it, or before the first output step).
export function parseLogProgress(logText: string): LogProgress | null {
  const matches = logText.matchAll(/\[Info\]\s*Step:\s*(\d+)\s*\/\s*(\d+)/g);
  let last: RegExpMatchArray | null = null;
  for (const match of matches) last = match;
  if (!last) return null;

  const currentStep = Number(last[1]);
  const totalSteps = Number(last[2]);
  if (!totalSteps) return null;

  return {
    percent: Math.min(100, Math.round((100 * currentStep) / totalSteps)),
    currentStep,
    totalSteps
  };
}
