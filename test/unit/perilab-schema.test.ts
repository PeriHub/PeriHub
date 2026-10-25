// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest';
import {
  NATIVE_KEYS,
  coerce,
  damageNativeKeys,
  enumOf,
  modelNames,
  node,
  paramsFor,
  pick,
  sections,
  solverNames,
  widgetOf
} from '../../src/lib/perilab/schema';

describe('perilab schema helpers', () => {
  it('lists registered model and solver names', () => {
    expect(modelNames(sections.material)).toContain('Correspondence Plastic');
    expect(modelNames(sections.damage)).toContain('Critical Stretch');
    expect(modelNames(sections.contact)).toContain('Penalty Contact');
    expect(solverNames()).toEqual(expect.arrayContaining(['Verlet', 'Static']));
  });

  it('unions the keys of every selected model and drops native ones', () => {
    const plastic = paramsFor(sections.material, ['Correspondence Plastic'], []);
    expect(plastic).toHaveProperty('Yield Stress');
    const both = paramsFor(sections.material, ['PD Solid Elastic', 'Correspondence Plastic'], []);
    expect(both).toHaveProperty('Yield Stress');
    const native = paramsFor(sections.material, ['Correspondence Plastic'], NATIVE_KEYS.material);
    expect(native).not.toHaveProperty('Yield Stress');
    expect(native).not.toHaveProperty('Material Model');
    expect(native).not.toHaveProperty('Globals');
  });

  it('skips objects and arrays, keeps scalar unions', () => {
    const solver = paramsFor(sections.solver, [], []);
    expect(solver).not.toHaveProperty('Verlet');
    expect(solver).not.toHaveProperty('Fallback');
    expect(solver).toHaveProperty('Degradation Models');
    const bc = paramsFor(sections.boundaryCondition, [], []);
    expect(bc).toHaveProperty('Value');
  });

  it('reads solver sub-sections', () => {
    expect(paramsFor(node(['Newmark'], sections.solver), [], [])).toHaveProperty('Newmark Alpha');
  });

  it('picks options with fallback and keeps the current value', () => {
    expect(pick([], ['a'], 'b')).toEqual(['a', 'b']);
    expect(pick(['x'], ['a'], ['x', 'y'])).toEqual(['x', 'y']);
    expect(pick(['x'], ['a'], null)).toEqual(['x']);
    expect(enumOf(node(['Type'], sections.boundaryCondition))).toEqual(
      expect.arrayContaining(['Dirichlet', 'Neumann'])
    );
  });

  it('chooses widgets and coerces input text', () => {
    expect(widgetOf({ type: 'boolean' })).toBe('toggle');
    expect(widgetOf({ type: 'integer' })).toBe('number');
    expect(widgetOf({ type: 'string', enum: ['a'] })).toBe('select');
    expect(widgetOf({ type: ['number', 'string'] })).toBe('text');
    expect(coerce({ type: 'number' }, ' 2.5 ')).toBe(2.5);
    expect(coerce({ type: ['number', 'string'] }, '10*t')).toBe('10*t');
    expect(coerce({ type: ['number', 'string'] }, '3')).toBe(3);
    expect(coerce({ type: 'string' }, '3')).toBe('3');
    expect(coerce({ type: 'number' }, '  ')).toBeUndefined();
    expect(coerce({ type: 'integer' }, '3')).toBe(3);
    expect(coerce({ type: 'integer' }, '2.5')).toBe('2.5');
  });

  it('keeps Critical Value editable only for damage models without a native field', () => {
    expect(damageNativeKeys('Critical Stretch')).toContain('Critical Value');
    expect(damageNativeKeys('Critical Energy Anisotropic')).not.toContain('Critical Value');
  });
});
