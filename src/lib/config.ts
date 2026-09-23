// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * Central runtime configuration.
 *
 * In dev, values come from Vite env vars (.env, .env.local — see .env.example).
 * In production builds, the literal `_VALUE` placeholders below are left in the
 * compiled JS on purpose and get substituted by `frontend/entrypoint.sh` at
 * container startup (same mechanism the old Quasar build used), so the same
 * Docker image can be deployed with different Keycloak/cluster settings
 * without rebuilding.
 */

const dev = import.meta.env.DEV;

function resolve(devValue: string | undefined, placeholder: string): string {
  if (dev) return devValue ?? '';
  // Left intact for entrypoint.sh to sed-replace in the built bundle.
  return placeholder;
}

export const config = {
  dev,
  apiBase: dev ? 'http://localhost:8000' : 'api',
  trial: resolve(import.meta.env.VITE_TRIAL, 'TRIAL_VALUE') === 'True',
  clusterUrl: resolve(import.meta.env.VITE_CLUSTER_URL, 'CLUSTER_URL_VALUE'),
  keycloakUrl: resolve(import.meta.env.VITE_KEYCLOAK_URL, 'KEYCLOAK_URL_VALUE'),
  realm: resolve(import.meta.env.VITE_REALM, 'REALM_VALUE'),
  clientId: resolve(import.meta.env.VITE_CLIENT_ID, 'CLIENT_ID_VALUE')
};
