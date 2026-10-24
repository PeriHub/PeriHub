// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * PeriLab's input-deck JSON Schema (`npm run perilab-schema` -> schema.json), read for the expansions' option
 * lists and their "Additional PeriLab parameters" (PerilabParams.svelte). PeriHub's own fields stay hand-written
 * and are listed in NATIVE_KEYS so they aren't offered twice; the backend writer merges the rest from each item's
 * `extra` (and Solver's `solverOptions`) with native keys winning. Unknown sections/names give empty results
 * (fail open), so a schema missing a module never breaks a panel.
 */

import schemaJson from './schema.json';

export interface SchemaProp {
  type?: string | string[];
  enum?: unknown[];
  examples?: unknown[];
  default?: unknown;
  minimum?: number;
  maximum?: number;
  description?: string;
  oneOf?: SchemaProp[];
  required?: string[];
  properties?: Record<string, SchemaProp>;
  additionalProperties?: SchemaProp | boolean;
  allOf?: { if: { properties: Record<string, { const: string }> }; then: SchemaProp }[];
  'x-perilab-eval'?: boolean;
}

const root = (schemaJson as unknown as SchemaProp).properties?.PeriLab;

/** Walks `properties[segment]`; `'*'` steps into `additionalProperties` (named entries such as materials). */
export function node(path: string[], from: SchemaProp | undefined = root): SchemaProp | undefined {
  let current = from;
  for (const segment of path) {
    const next = segment === '*' ? current?.additionalProperties : current?.properties?.[segment];
    current = typeof next === 'object' ? next : undefined;
  }
  return current;
}

export const sections = {
  material: node(['Models', 'Material Models', '*']),
  damage: node(['Models', 'Damage Models', '*']),
  thermal: node(['Models', 'Thermal Models', '*']),
  additive: node(['Models', 'Additive Models', '*']),
  contact: node(['Contact', '*']),
  block: node(['Blocks', '*']),
  output: node(['Outputs', '*']),
  boundaryCondition: node(['Boundary Conditions', '*']),
  bondFilter: node(['Discretization', 'Bond Filters', '*']),
  discretization: node(['Discretization']),
  solver: node(['Solver'])
};

/** Names of the registered models of a named-entry section (its `allOf` `if ... const` branches). */
export function modelNames(entry?: SchemaProp): string[] {
  return (entry?.allOf ?? []).flatMap((c) => Object.values(c.if.properties).map((p) => p.const));
}

/** Registered solvers: the Solver section requires exactly one of these sub-sections. */
export function solverNames(): string[] {
  return (sections.solver?.oneOf ?? []).flatMap((c) => c.required ?? []);
}

const SCALARS = new Set(['number', 'integer', 'boolean', 'string']);

function isScalar(prop: SchemaProp): boolean {
  if (prop.oneOf) return prop.oneOf.every(isScalar);
  const types = [prop.type].flat();
  return types.length > 0 && types.every((t) => t !== undefined && SCALARS.has(t));
}

/**
 * Keys a user can set on one entry: the section's shared keys plus those of every named model (composite
 * `A + B` materials get the union), without `Globals`, `nativeKeys` and non-scalar keys (those need custom UX).
 */
export function paramsFor(
  entry: SchemaProp | undefined,
  names: readonly string[],
  nativeKeys: readonly string[]
): Record<string, SchemaProp> {
  const merged: Record<string, SchemaProp> = { ...entry?.properties };
  for (const branch of entry?.allOf ?? []) {
    if (Object.values(branch.if.properties).some((p) => names.includes(p.const))) {
      Object.assign(merged, branch.then.properties);
    }
  }
  return Object.fromEntries(
    Object.entries(merged).filter(
      ([key, prop]) => key !== 'Globals' && !nativeKeys.includes(key) && isScalar(prop)
    )
  );
}

export function enumOf(prop?: SchemaProp): string[] {
  return (prop?.enum ?? prop?.examples ?? []).map(String);
}

/** `list` (or `fallback` while the schema has none), plus saved values missing from it so old configs render. */
export function pick(
  list: readonly string[],
  fallback: readonly string[],
  current?: string | readonly string[] | null
): string[] {
  const options = list.length ? [...list] : [...fallback];
  for (const value of [current ?? []].flat()) {
    if (value && !options.includes(value)) options.push(value);
  }
  return options;
}

export type Widget = 'number' | 'toggle' | 'select' | 'text';

export function widgetOf(prop: SchemaProp): Widget {
  if (enumOf(prop).length) return 'select';
  if (prop.type === 'boolean') return 'toggle';
  if (prop.type === 'number' || prop.type === 'integer') return 'number';
  return 'text';
}

/** Input text -> deck value: blank unsets (PeriLab's default applies), numbers stay numbers where allowed. */
export function coerce(prop: SchemaProp, raw: string): string | number | undefined {
  const text = raw.trim();
  if (text === '') return undefined;
  const types = prop.oneOf
    ? prop.oneOf.flatMap((o) => [o.type ?? []].flat())
    : [prop.type ?? []].flat();
  const number = Number(text);
  if ((types.includes('number') || types.includes('integer')) && Number.isFinite(number))
    return number;
  return text;
}

const axes = (prefix: string) => ['X', 'Y', 'Z'].map((axis) => `${prefix} ${axis}`);
const stiffnessKeys = [1, 2, 3, 4, 5, 6].flatMap((i) =>
  [1, 2, 3, 4, 5, 6].filter((j) => j >= i).map((j) => `C${i}${j}`)
);

/** YAML keys each expansion already renders and backend/app/support/writer/yaml_writer_perilab.py writes. */
export const NATIVE_KEYS = {
  material: [
    'Material Model',
    'Symmetry',
    ...stiffnessKeys,
    "Young's Modulus",
    ...axes("Young's Modulus"),
    "Poisson's Ratio",
    "Poisson's Ratio XY",
    "Poisson's Ratio YZ",
    "Poisson's Ratio XZ",
    'Shear Modulus',
    'Shear Modulus XY',
    'Shear Modulus YZ',
    'Shear Modulus XZ',
    'Bulk Modulus',
    'Zero Energy Control',
    'Yield Stress',
    'Number of State Vars',
    'Number of Properties',
    'Compute Partial Stress',
    'Use Collocation Nodes'
  ],
  damage: [
    'Damage Model',
    'Critical Value',
    'Critical Von Mises Stress',
    'Critical Damage',
    'Threshold Damage',
    'Critical Damage To Neglect',
    'Interblock Damage',
    'Anisotropic Damage',
    'Only Tension',
    'Thickness'
  ],
  thermal: [
    'Thermal Model',
    'Type',
    'Thermal Conductivity',
    'Thermal Conductivity Print Bed',
    'Print Bed Temperature',
    'Print Bed Z Coordinate',
    'Environmental Temperature',
    'Heat Transfer Coefficient',
    'Thermal Expansion Coefficient'
  ],
  additive: ['Additive Model', 'Print Temperature'],
  contact: ['Type', 'Contact Radius', 'Contact Stiffness', 'Contact Groups'],
  block: [
    'Block ID',
    'Material Model',
    'Damage Model',
    'Thermal Model',
    'Additive Model',
    'Horizon',
    'Density',
    'Specific Heat Capacity'
  ],
  output: [
    'Output File Type',
    'Output Filename',
    'Initial Output Step',
    'Output Frequency',
    'Number of Output Steps',
    'Write After Damage',
    'Output Variables'
  ],
  boundaryCondition: ['Type', 'Variable', 'Node Set', 'Step ID', 'Coordinate', 'Value'],
  bondFilter: [
    'Type',
    ...axes('Normal'),
    'Allow Contact',
    ...axes('Lower Left Corner'),
    ...axes('Bottom Unit Vector'),
    'Bottom Length',
    'Side Length',
    ...axes('Center'),
    'Radius'
  ],
  discretization: [
    'Type',
    'Node Sets',
    'Input Mesh File',
    'Gcode',
    'Bond Filters',
    'Distribution Type'
  ],
  solver: [
    'Step ID',
    'Material Models',
    'Damage Models',
    'Thermal Models',
    'Additive Models',
    'Initial Time',
    'Final Time',
    'Additional Time',
    'Maximum Damage',
    'Calculate Cauchy',
    'Calculate von Mises stress',
    'Calculate Strain',
    'Stop before damage initiation'
  ]
} as const satisfies Record<string, readonly string[]>;

/** Sub-section keys the Verlet/Static branches of the writer handle; other solvers are fully schema-driven. */
export const SOLVER_NATIVE_KEYS: Record<string, readonly string[]> = {
  Verlet: [
    'Fixed dt',
    'Safety Factor',
    'Numerical Damping',
    'Adapt dt',
    'Stable Step Difference',
    'Maximum Bond Difference',
    'Stable Bond Difference'
  ],
  Static: [
    'Maximum number of iterations',
    'Show solver iteration',
    'Residual tolerance',
    'Solution tolerance',
    'Linear Start Value',
    'Residual scaling',
    'm'
  ]
};

const NATIVE_DAMAGE_MODELS = ['Critical Stretch', 'Critical Energy', 'Von Mises Stress'];

/** The writer only fills `Critical Value` for its own damage models; others take it from `extra`. */
export function damageNativeKeys(model: string | null | undefined): readonly string[] {
  return NATIVE_DAMAGE_MODELS.includes(model ?? '')
    ? NATIVE_KEYS.damage
    : NATIVE_KEYS.damage.filter((key) => key !== 'Critical Value');
}
