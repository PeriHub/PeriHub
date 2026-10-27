import { describe, expect, it } from 'vitest';
import {
  AUTO_KEYS,
  CUSTOM_KEYS,
  coerce,
  enumOf,
  missingRequired,
  modelNames,
  node,
  paramsFor,
  pick,
  sections,
  solverNames,
  splitModels,
  joinModels,
  widgetOf,
  propInfo,
  whenMet,
  type SchemaProp
} from '../../src/lib/perilab/schema';

describe('perilab schema helpers', () => {
  it('lists registered model and solver names', () => {
    expect(modelNames(sections.material)).toContain('Correspondence Plastic');
    expect(modelNames(sections.damage)).toContain('Critical Stretch');
    expect(modelNames(sections.contact)).toContain('Penalty Contact');
    expect(solverNames()).toEqual(expect.arrayContaining(['Verlet', 'Static']));
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

  it('splits PeriLab descriptions into text and facts', () => {
    expect(
      propInfo({
        type: 'number',
        minimum: 0,
        default: 1,
        description: 'elastic stiffness; quantity: stress (in your consistent unit system)'
      })
    ).toEqual({ text: 'elastic stiffness', facts: ['≥ 0', 'default 1', 'stress'] });
    expect(
      propInfo({
        oneOf: [
          { type: 'number', minimum: 0 },
          { type: 'string', description: 'data file path' }
        ]
      })
    ).toEqual({ text: '', facts: ['≥ 0', 'or data file'] });
    expect(propInfo({ type: 'boolean', default: false })).toEqual({
      text: '',
      facts: ['default off']
    });
    expect(propInfo({ type: 'string', description: 'one of: a, b' })).toEqual({
      text: '',
      facts: []
    });
  });
});

// A hand-written entry in PeriLab's schema shape, so these tests don't depend on schema.json's contents.
const entry: SchemaProp = {
  required: ['Model'],
  properties: {
    Model: { type: 'string' },
    Symmetry: { type: 'string', enum: ['isotropic', 'orthotropic'], default: 'isotropic' },
    'Young X': { type: 'number', 'x-perilab-when': { Symmetry: ['orthotropic'] } },
    Steps: { type: 'integer', 'x-perilab-when': { $solver: ['Static', 'Newmark'] } },
    Nested: { type: 'object', properties: { A: { type: 'number' } } },
    Map: { type: 'object', additionalProperties: { type: 'number' } },
    List: { type: 'array' },
    Globals: { type: 'object' }
  },
  allOf: [
    {
      if: { properties: { Model: { const: 'Plastic' } } },
      then: { required: ['Yield'], properties: { Yield: { type: 'number' } } }
    },
    { if: { properties: { Symmetry: { const: 'orthotropic' } } }, then: { required: ['Young X'] } }
  ]
};

describe('paramsFor', () => {
  it('keeps declaration order, scalars and nested objects; drops maps, arrays, Globals and custom keys', () => {
    const { props } = paramsFor(entry, [], ['Model']);
    expect(Object.keys(props)).toEqual(['Symmetry', 'Nested']);
  });

  it('merges model branches and their required keys', () => {
    const offered = paramsFor(entry, ['Plastic']);
    expect(offered.props).toHaveProperty('Yield');
    expect([...offered.required]).toEqual(expect.arrayContaining(['Model', 'Yield']));
  });

  it('applies x-perilab-when from sibling values, defaults and the solver', () => {
    expect(paramsFor(entry, []).props).not.toHaveProperty('Young X');
    const ortho = paramsFor(entry, [], [], { values: { Symmetry: 'Orthotropic' } });
    expect(ortho.props).toHaveProperty('Young X');
    expect(ortho.required.has('Young X')).toBe(true);
    expect(paramsFor(entry, [], [], { solver: 'Verlet' }).props).not.toHaveProperty('Steps');
    expect(paramsFor(entry, [], [], { solver: 'Static' }).props).toHaveProperty('Steps');
  });

  it('whenMet needs every condition and treats an unset key without default as not met', () => {
    const prop: SchemaProp = { 'x-perilab-when': { A: ['x'], B: ['y'] } };
    const siblings: Record<string, SchemaProp> = { A: {}, B: {} };
    expect(whenMet(prop, siblings, { values: { A: 'x', B: 'y' } })).toBe(true);
    expect(whenMet(prop, siblings, { values: { A: 'x' } })).toBe(false);
  });
});

describe('missingRequired', () => {
  it('lists required keys without a value, minus auto-filled ones', () => {
    const offered = paramsFor(entry, ['Plastic']);
    expect(missingRequired(offered, { Model: 'Plastic' })).toEqual(['Yield']);
    expect(missingRequired(offered, { Model: '', Yield: 1 })).toEqual(['Model']);
    expect(missingRequired(offered, {}, ['Model', 'Yield'])).toEqual([]);
  });
});

describe('model name lists', () => {
  it('splits and joins composite model strings', () => {
    expect(splitModels('Correspondence Elastic + Correspondence Plastic')).toEqual([
      'Correspondence Elastic',
      'Correspondence Plastic'
    ]);
    expect(splitModels(undefined)).toEqual([]);
    expect(joinModels(['A', 'B'])).toBe('A + B');
    expect(joinModels([])).toBeUndefined();
  });

  it('reads required groups from the real schema', () => {
    const outputs = paramsFor(sections.output, [], CUSTOM_KEYS.output);
    expect(outputs.groups.map((g) => g.keys)).toEqual([
      ['Output Frequency', 'Number of Output Steps']
    ]);
    expect(missingRequired(outputs, {}, AUTO_KEYS.output)).toEqual([
      'one of Output Frequency, Number of Output Steps'
    ]);
    expect(missingRequired(outputs, { 'Output Frequency': 10 }, AUTO_KEYS.output)).toEqual([]);

    const iso = { 'Material Model': 'PD Solid Elastic', Symmetry: 'isotropic' };
    const solid = paramsFor(sections.material, ['PD Solid Elastic'], [], { values: iso });
    expect(missingRequired(solid, { ...iso, "Young's Modulus": 1 })).toEqual([
      "two of Young's Modulus, Poisson's Ratio, Bulk Modulus, Shear Modulus"
    ]);
    expect(
      missingRequired(solid, { ...iso, "Young's Modulus": 1, "Poisson's Ratio": 0.3 })
    ).toEqual([]);
    const bb = { 'Material Model': 'Bond-based Elastic', Symmetry: 'isotropic' };
    const bondBased = paramsFor(sections.material, ['Bond-based Elastic'], [], { values: bb });
    expect(bondBased.groups.map((g) => g.min)).toEqual([1]);
    expect(missingRequired(bondBased, { ...bb, 'Bulk Modulus': 1 })).toEqual([]);
  });

  it('applies enum branches (orthotropic symmetry requires its constants)', () => {
    const values = { 'Material Model': 'PD Solid Elastic', Symmetry: 'orthotropic' };
    const ortho = paramsFor(sections.material, ['PD Solid Elastic'], CUSTOM_KEYS.material, {
      values
    });
    expect(ortho.required).toContain("Young's Modulus X");
    expect(ortho.groups).toEqual([]);
    expect(modelNames(sections.material)).not.toContain(undefined);
  });

  it('declares custom and auto keys per section', () => {
    expect(CUSTOM_KEYS.block).toContain('Material Model');
    expect(AUTO_KEYS.output).toContain('Output Filename');
  });
});
