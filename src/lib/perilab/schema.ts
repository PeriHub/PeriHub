// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * PeriLab's input-deck JSON Schema (`npm run perilab-schema` -> schema.json) drives every PeriLab parameter in
 * PeriHub: SchemaParams.svelte renders an entry's keys from `paramsFor`, values live in the entry's `params`
 * (YAML key -> value), and the backend writer merges them into the deck. Expansions render only `CUSTOM_KEYS`
 * themselves. Unknown sections/names give empty results (fail open), so a schema missing a module never breaks a
 * panel.
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
  allOf?: {
    if: { properties: Record<string, { const: string }> };
    then: SchemaProp;
  }[];
  'x-perilab-eval'?: boolean;
  /** Read only if every listed sibling key (or `$solver`, the chosen solver) has one of the listed values. */
  'x-perilab-when'?: Record<string, string[]>;
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
  compute: node(['Compute Class Parameters', '*']),
  contactGlobals: node(['Contact', 'Globals']),
  solver: node(['Solver']),
  multistepSolver: node(['Multistep Solver', '*'])
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

export interface PropInfo {
  /** PeriLab's own words, without the parts shown as facts. */
  text: string;
  /** Short machine facts: valid range, default, data-file option, physical quantity. */
  facts: string[];
}

const QUANTITY = /^quantity: (.+?) \(in your consistent unit system\)$/;

/**
 * Tooltip content for a parameter. PeriLab joins description parts with "; " and appends the quantity and,
 * for enums, "one of: ..." (already visible in the select), so those become facts or are dropped.
 */
export function propInfo(prop: SchemaProp): PropInfo {
  const text: string[] = [];
  let quantity: string | undefined;
  for (const part of (prop.description ?? '').split('; ')) {
    const match = QUANTITY.exec(part);
    if (match) quantity = match[1];
    else if (part && !part.startsWith('one of:')) text.push(part);
  }
  const branch = prop.oneOf?.find((o) => o.minimum != null || o.maximum != null);
  const min = prop.minimum ?? branch?.minimum;
  const max = prop.maximum ?? branch?.maximum;
  const facts: string[] = [];
  if (min != null && max != null) facts.push(`${min} – ${max}`);
  else if (min != null) facts.push(`≥ ${min}`);
  else if (max != null) facts.push(`≤ ${max}`);
  if (prop.default != null) {
    facts.push(
      `default ${typeof prop.default === 'boolean' ? (prop.default ? 'on' : 'off') : prop.default}`
    );
  }
  if (prop.oneOf?.some((o) => o.description === 'data file path')) facts.push('or data file');
  if (quantity) facts.push(quantity);
  return { text: text.join('. '), facts };
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
  if (types.includes('number') && Number.isFinite(number)) return number;
  if (types.includes('integer') && Number.isInteger(number)) return number;
  return text;
}

export interface Context {
  /** The entry's current values, for `x-perilab-when` conditions on sibling keys and `Type`-dependent branches. */
  values?: Record<string, unknown>;
  /** The chosen solver sub-section, for `$solver` conditions. */
  solver?: string;
}

export interface Offered {
  props: Record<string, SchemaProp>;
  required: Set<string>;
}

const same = (a: unknown, b: unknown) => String(a).toLowerCase() === String(b).toLowerCase();

export function isSet(value: unknown): boolean {
  return value != null && !(typeof value === 'string' && value.trim() === '');
}

/** `x-perilab-when`: every condition key's value (else its schema default) is one of the listed values. */
export function whenMet(
  prop: SchemaProp,
  siblings: Record<string, SchemaProp>,
  ctx: Context
): boolean {
  return Object.entries(prop['x-perilab-when'] ?? {}).every(([key, allowed]) => {
    const value = key === '$solver' ? ctx.solver : (ctx.values?.[key] ?? siblings[key]?.default);
    return isSet(value) && allowed.some((option) => same(option, value));
  });
}

function offerable(prop: SchemaProp): boolean {
  return isScalar(prop) || (prop.type === 'object' && !!prop.properties);
}

/** An `allOf` branch applies if every `if` const is a selected model name or the entry's value of that key. */
function branchApplies(
  branch: NonNullable<SchemaProp['allOf']>[number],
  names: readonly string[],
  ctx: Context
): boolean {
  return Object.entries(branch.if.properties).every(
    ([key, cond]) => names.includes(cond.const) || same(ctx.values?.[key] ?? '', cond.const)
  );
}

/**
 * Keys a user can set on one entry, in PeriLab's declaration order: the section's shared keys plus those of every
 * applying `allOf` branch (selected models, `Type`-dependent keys), without `Globals`, `custom` keys (rendered by
 * the expansion), maps/arrays (need custom UX) and keys whose `x-perilab-when` isn't met. `required` holds the
 * required keys among them and among `custom`.
 */
export function paramsFor(
  entry: SchemaProp | undefined,
  names: readonly string[],
  custom: readonly string[] = [],
  ctx: Context = {}
): Offered {
  const merged: Record<string, SchemaProp> = { ...entry?.properties };
  const required = new Set(entry?.required ?? []);
  for (const branch of entry?.allOf ?? []) {
    if (!branchApplies(branch, names, ctx)) continue;
    Object.assign(merged, branch.then.properties);
    branch.then.required?.forEach((key) => required.add(key));
  }
  const applies = (key: string) => !merged[key] || whenMet(merged[key]!, merged, ctx);
  const props = Object.fromEntries(
    Object.entries(merged).filter(
      ([key, prop]) => key !== 'Globals' && !custom.includes(key) && offerable(prop) && applies(key)
    )
  );
  return {
    props,
    required: new Set(
      [...required].filter((key) => (key in props || custom.includes(key)) && applies(key))
    )
  };
}

/** Required keys without a value; `auto` keys are filled by PeriHub (writer/generator) and never missing. */
export function missingRequired(
  offered: Offered,
  values: Record<string, unknown>,
  auto: readonly string[] = []
): string[] {
  return [...offered.required].filter((key) => !auto.includes(key) && !isSet(values[key]));
}

/** PeriLab's composite model strings ("A + B") <-> the list of selected models. */
export function splitModels(value: unknown): string[] {
  return typeof value === 'string'
    ? value
        .split('+')
        .map((name) => name.trim())
        .filter(Boolean)
    : [];
}

export function joinModels(names: readonly (string | number)[]): string | undefined {
  return names.length ? names.join(' + ') : undefined;
}

/** Keys each expansion renders itself (references to other entries, composite pickers, lists, table columns). */
export const CUSTOM_KEYS = {
  material: ['Material Model'],
  damage: ['Damage Model'],
  thermal: ['Thermal Model'],
  additive: ['Additive Model'],
  contact: ['Type', 'Contact Groups'],
  contactGroup: ['Master Block ID', 'Slave Block ID'],
  block: [
    'Block ID',
    'Material Model',
    'Damage Model',
    'Thermal Model',
    'Additive Model',
    'Density',
    'Horizon',
    'Specific Heat Capacity',
    // Hidden: PeriHub has no FEM, degradation or pre-calculation sections to point at.
    'FEM',
    'Degradation Model',
    'Pre Calculation Model'
  ],
  output: ['Output Filename', 'Output Variables', 'Output File Type'],
  boundaryCondition: ['Type', 'Variable', 'Node Set', 'Step ID', 'Coordinate', 'Value'],
  bondFilter: ['Type'],
  discretization: ['Type', 'Input Mesh File', 'Node Sets', 'Gcode', 'Bond Filters'],
  compute: ['Compute Class', 'Block', 'Node Set'],
  solver: ['Step ID']
} as const satisfies Record<string, readonly string[]>;

/** Required keys PeriHub fills itself (writer or generator), so they never count as missing. */
export const AUTO_KEYS = {
  block: ['Block ID'],
  boundaryCondition: ['Node Set', 'Step ID'],
  output: ['Output Filename', 'Output Variables'],
  discretization: ['Type', 'Input Mesh File'],
  contact: ['Contact Groups'],
  compute: ['Node Set'],
  solver: ['Step ID']
} as const satisfies Record<string, readonly string[]>;
