// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * Required PeriLab keys without a value, per ModelData section - for the panel badges (ExpansionComp) and the
 * Generate/Run warning. Mirrors how each expansion calls paramsFor (selected models, solver), so a key counts as
 * missing exactly where the form marks it.
 */

import type { ModelData } from '$lib/client';
import {
  AUTO_KEYS,
  missingRequired,
  node,
  paramsFor,
  sections,
  splitModels,
  type SchemaProp
} from './schema';

type Values = Record<string, unknown>;

function check(
  section: SchemaProp | undefined,
  label: string,
  values: Values | undefined,
  names: readonly string[] = [],
  auto: readonly string[] = [],
  solver?: string
): string[] {
  const v = values ?? {};
  return missingRequired(paramsFor(section, names, [], { values: v, solver }), v, auto).map(
    (key) => `${label}: ${key}`
  );
}

function entries<T extends { name: string; params?: Values }>(
  list: T[] | null | undefined,
  section: SchemaProp | undefined,
  names: (entry: T) => readonly string[] = () => [],
  auto: readonly string[] = []
): string[] {
  return (list ?? []).flatMap((e) => check(section, e.name, e.params, names(e), auto));
}

export function missingBySection(data: ModelData): Partial<Record<string, string[]>> {
  const generated = data.model.meshSource !== 'upload';
  const solverSection = data.solvers.length > 1 ? sections.multistepSolver : sections.solver;
  return {
    discretization: check(
      sections.discretization,
      'Discretization',
      data.discretization?.params,
      [],
      AUTO_KEYS.discretization
    ),
    blocks: entries(data.blocks, sections.block, () => [], [
      ...AUTO_KEYS.block,
      ...(generated ? ['Horizon'] : [])
    ]),
    materials: entries(data.materials, sections.material, (m) =>
      splitModels(m.params?.['Material Model'])
    ),
    thermal: entries(data.thermal, sections.thermal, (t) =>
      splitModels(t.params?.['Thermal Model'])
    ),
    additive: entries(data.additive, sections.additive, (a) => [
      String(a.params?.['Additive Model'] ?? '')
    ]),
    damages: entries(data.damages, sections.damage, (d) => [
      String(d.params?.['Damage Model'] ?? '')
    ]),
    contact: entries(
      data.contact?.contactModels,
      sections.contact,
      (c) => [String(c.params?.['Type'] ?? '')],
      AUTO_KEYS.contact
    ),
    boundaryConditions: entries(
      data.boundaryConditions.conditions,
      sections.boundaryCondition,
      () => [],
      AUTO_KEYS.boundaryCondition
    ),
    bondFilters: entries(data.bondFilters, sections.bondFilter),
    outputs: [
      ...entries(data.outputs, sections.output, () => [], AUTO_KEYS.output),
      ...entries(data.computes, sections.compute, () => [], AUTO_KEYS.compute)
    ],
    solvers: data.solvers.flatMap((s) => {
      const label = s.name ?? `Solver ${s.solverId ?? s.stepId}`;
      return [
        ...check(solverSection, label, s.params, [], AUTO_KEYS.solver, s.solvertype),
        ...check(node([s.solvertype], solverSection), label, s.solverOptions)
      ];
    })
  };
}
