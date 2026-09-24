// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

/**
 * Central runtime configuration.
 *
 * `config` covers the two things that genuinely have to be decided at
 * build/dev time (are we in `npm run dev`, and what's the API base URL).
 * Everything else that used to be duplicated here as its own VITE_* env
 * var (TRIAL, CLUSTER_URL, OAUTH_ENABLED) is now fetched once from the
 * backend's single source of truth (GET /config/public, see
 * backend/app/routers/config.py) via `loadPublicConfig()` - see
 * $lib/auth/oauth.ts's initAuth(), which awaits it before anything else
 * runs. That backend endpoint already reads the same env vars from its
 * own .env, so there's exactly one place to set them now instead of two.
 */

const dev = import.meta.env.DEV;

export const config = {
  dev,
  apiBase: dev ? 'http://localhost:8000' : 'api'
};

interface PublicConfigResponse {
  deployment_mode: string;
  trial: boolean;
  cluster_url: string;
  oauth_enabled: boolean;
}

/**
 * Populated by loadPublicConfig(). Starts with safe empty defaults so
 * nothing throws if a component reads it before that fetch resolves or if
 * the fetch fails - trial/OAuth just come up "off" rather than the app
 * crashing.
 */
export const publicConfig = {
  trial: false,
  clusterUrl: '',
  oauthEnabled: false
};

let loaded = false;

/**
 * Fetches GET /config/public and populates `publicConfig`. Idempotent and
 * safe to call more than once (e.g. once from initAuth() on first load,
 * again from the OAuth callback page) - only the first call actually
 * hits the network.
 */
export async function loadPublicConfig(): Promise<void> {
  if (loaded) return;
  try {
    const response = await fetch(`${config.apiBase}/config/public`);
    if (!response.ok) {
      throw new Error(`GET /config/public -> HTTP ${response.status}`);
    }
    const data = (await response.json()) as PublicConfigResponse;
    publicConfig.trial = data.trial;
    publicConfig.clusterUrl = data.cluster_url ?? '';
    publicConfig.oauthEnabled = data.oauth_enabled ?? false;
    loaded = true;
  } catch (error) {
    // Deliberately non-fatal: the app still boots with everything "off"
    // (no trial identity, no OAuth) rather than a blank screen if the
    // backend is briefly unreachable at load time. Not marking `loaded`
    // here so a later call (e.g. from the OAuth callback page) gets a
    // chance to retry instead of being stuck with empty defaults forever.
    console.error('Failed to load public config from backend, using defaults:', error);
  }
}
