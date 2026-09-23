// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * "Is this section's required data filled in" checks for ExpansionComp's
 * panel-completeness indicators, driven by the backend's actual Pydantic
 * schemas (via the generated `$<Name>` consts in `$lib/client/schemas.gen`)
 * rather than a second, hand-maintained list of required fields that could
 * silently drift from `support/base_models.py`.
 *
 * This deliberately only checks *presence* (required fields aren't
 * undefined/null/empty-string), not full JSON-Schema validation (types,
 * ranges, enum membership, ...) - see PROFESSIONALIZATION.md's form
 * validation recommendation for that larger follow-up. This is a "does the
 * panel need attention" indicator, not a submit-time validator.
 */

import * as schemas from '$lib/client/schemas.gen';

interface JsonSchemaLike {
  properties?: Record<string, unknown>;
  required?: string[];
}

function getSchema(name: string): JsonSchemaLike | null {
  const key = `$${name}` as keyof typeof schemas;
  const schema = schemas[key] as JsonSchemaLike | undefined;
  return schema ?? null;
}

function isPresent(value: unknown): boolean {
  if (value == null) return false;
  if (typeof value === 'string') return value.trim() !== '';
  if (Array.isArray(value)) return true; // presence, not non-emptiness - empty arrays are valid for some fields
  return true;
}

function requiredFieldsPresent(schema: JsonSchemaLike, data: Record<string, unknown>): boolean {
  const required = schema.required ?? [];
  return required.every((field) => isPresent(data[field]));
}

/**
 * For a single-object section (Model, Discretization, Thermal, Additive,
 * Contact, BoundaryConditions, Output-as-object-like sections, Job,
 * Deviations): true if the schema's required fields are all present on
 * `data`, or if the schema can't be found (fails open rather than showing
 * every panel as permanently incomplete if a schema gets renamed).
 */
export function isObjectSectionComplete(schemaName: string, data: unknown): boolean {
  const schema = getSchema(schemaName);
  if (!schema) return true;
  if (data == null || typeof data !== 'object') return false;
  return requiredFieldsPresent(schema, data as Record<string, unknown>);
}

/**
 * For a list section (Material, Damage, Block, Solver, BondFilters, Output):
 * true only if the list is non-empty AND every item satisfies the schema's
 * required fields. An empty list is treated as incomplete since every one
 * of these sections needs at least one entry for the model to be valid
 * (e.g. you can't generate a model with zero materials or zero solvers).
 */
export function isArraySectionComplete(schemaName: string, data: unknown): boolean {
  const schema = getSchema(schemaName);
  if (!schema) return true;
  if (!Array.isArray(data) || data.length === 0) return false;
  return data.every((item) => item != null && typeof item === 'object' && requiredFieldsPresent(schema, item));
}
