// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { sha256 } from 'js-sha256';
import { publicConfig, config, loadPublicConfig } from '$lib/config';
import { api } from '$lib/api/client';
import { OpenAPI } from '$lib/client';
import { defaultStore } from '$lib/stores/default-store.svelte';
import { authStore } from '$lib/stores/auth-store.svelte';

/**
 * Generic OAuth2/OIDC login (backend: routers/oauth.py, support/oidc_client.py).
 *
 * Works against any IdP that publishes a standard OIDC discovery document,
 * Keycloak included - there's no IdP-specific frontend code any more.
 * PeriHub's backend drives the authorization-code exchange itself, so all
 * the frontend does is:
 *   1. ask the backend for the IdP's authorization URL (/oauth/oidc/login)
 *      and redirect the browser there
 *   2. once the IdP redirects back to /auth/callback with `code` + `state`,
 *      hand `code` to the backend (/oauth/oidc/callback) and get back a
 *      PeriHub session token
 *   3. store that token and use it as a Bearer token on every request
 *
 * The PeriHub session token (not any IdP token) is what's persisted, so a
 * page reload just re-validates it via GET /auth/me instead of re-running
 * the whole redirect dance.
 */

const TOKEN_STORAGE_KEY = 'periHubSessionToken';
const STATE_STORAGE_KEY = 'periHubOAuthState';

interface MeResponse {
  user_id: string;
  email: string | null;
  display_name: string;
  role: string;
  auth_provider: string;
  org_id: string | null;
}

interface AuthorizationUrlResponse {
  authorization_url: string;
  state: string;
}

interface OidcAuthResponse {
  token: string;
  user_id: string;
  display_name: string;
  role: string;
}

/** Response shape shared by POST /auth/login and POST /auth/signup. */
interface LocalAuthResponse {
  token: string;
  user_id: string;
  display_name: string;
  role: string;
}

function browser() {
  return typeof window !== 'undefined';
}

/** Attaches the PeriHub session token as a Bearer token to every request. */
function applySessionToken(token: string) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  OpenAPI.HEADERS = { ...((OpenAPI.HEADERS as object) ?? {}), Authorization: `Bearer ${token}` };
}

/**
 * Asks the backend for the IdP's authorization URL, stashes `state` for the
 * callback page to verify, and sends the browser there. Never returns on
 * success (the browser navigates away).
 */
async function redirectToLogin(): Promise<void> {
  const response = await api.get<AuthorizationUrlResponse>('/oauth/oidc/login');
  sessionStorage.setItem(STATE_STORAGE_KEY, response.data.state);
  window.location.href = response.data.authorization_url;
}

/**
 * Exchanges the authorization `code` for a PeriHub session token, verifying
 * `state` against what /oauth/oidc/login handed out first (CSRF check -
 * see support/oidc_client.py's docstring). Called once, from
 * routes/auth/callback/+page.svelte.
 */
export async function completeOAuthCallback(code: string, state: string): Promise<void> {
  const expectedState = sessionStorage.getItem(STATE_STORAGE_KEY);
  sessionStorage.removeItem(STATE_STORAGE_KEY);
  if (!expectedState || expectedState !== state) {
    throw new Error('OAuth state mismatch - the login attempt could not be verified.');
  }
  const response = await api.get<OidcAuthResponse>('/oauth/oidc/callback', { params: { code } });
  localStorage.setItem(TOKEN_STORAGE_KEY, response.data.token);
}

/**
 * Local email/password login (backend: routers/auth.py's POST /auth/login).
 * Community deployments without OAuth configured use this instead of the
 * OIDC redirect flow - see routes/auth/login/+page.svelte, the only
 * caller. Throws with the backend's detail message on 401/403/409/422 so
 * the login/signup form can show it directly.
 */
export async function loginWithPassword(email: string, password: string): Promise<void> {
  const response = await api.post<LocalAuthResponse>('/auth/login', { email, password });
  localStorage.setItem(TOKEN_STORAGE_KEY, response.data.token);
}

/**
 * Local email/password signup (backend: routers/auth.py's POST /auth/signup).
 * Logs the new account straight in (the backend returns a session token
 * from signup the same way login does) rather than requiring a separate
 * login step afterwards.
 */
export async function signupWithPassword(
  email: string,
  password: string,
  displayName: string
): Promise<void> {
  const response = await api.post<LocalAuthResponse>('/auth/signup', {
    email,
    password,
    display_name: displayName
  });
  localStorage.setItem(TOKEN_STORAGE_KEY, response.data.token);
}

/**
 * Sets up auth for the app. Call from the root layout, client-side only.
 * - if OAuth isn't configured/licensed and this is a trial build, ask the
 *   backend for a random per-session identity (POST /auth/trial-id -
 *   replaces the old call out to the third-party randomuser.me API)
 * - if OAuth isn't configured and this *isn't* a trial build (i.e. a
 *   community deployment), look for a stored local-auth session token and
 *   validate it via GET /auth/me; if there isn't one (or it's no longer
 *   valid), send the browser to /auth/login instead of the IdP
 * - otherwise (OAuth configured), same as above but redirect to the IdP
 *   on a missing/invalid token instead of /auth/login
 */
export async function initAuth() {
  await loadPublicConfig();

  let uuid = 'user';
  let gravatarUrl = 'US';

  if (!publicConfig.oauthEnabled && publicConfig.trial) {
    console.log("I'm on a trial build");
    try {
      const response = await api.post('/auth/trial-id');
      uuid = response.data.username;
    } catch (e) {
      console.error('Failed to get a trial identity from the backend:', e);
    }
  } else {
    console.log(
      publicConfig.oauthEnabled ? 'Using OAuth/OIDC login' : 'Using local email/password login'
    );
    let profile: MeResponse | null = null;
    const storedToken = browser() ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;

    if (storedToken) {
      applySessionToken(storedToken);
      try {
        const response = await api.get<MeResponse>('/auth/me');
        profile = response.data;
        authStore.authenticated = true;
      } catch (e) {
        console.log('Stored session token is no longer valid, starting a new login:', e);
        localStorage.removeItem(TOKEN_STORAGE_KEY);
      }
    }

    if (!profile) {
      if (publicConfig.oauthEnabled) {
        try {
          await redirectToLogin();
        } catch (error) {
          console.error('Failed to start OAuth login:', error);
        }
      } else if (browser() && window.location.pathname !== '/auth/login') {
        window.location.href = '/auth/login';
      }
      return; // either the browser is navigating away, or login couldn't be started
    }

    uuid = profile.display_name;

    if (profile.email) {
      const email = profile.email;
      const emailHash = sha256(email);
      gravatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=404`;

      try {
        const response = await fetch(gravatarUrl);
        if (response.ok) {
          defaultStore.useGravatar = true;
          console.log('Gravatar image found for', email);
        } else {
          const emailParts = email.split('.');
          gravatarUrl =
            (emailParts[0]?.charAt(0).toUpperCase() ?? '') +
            (emailParts[1]?.charAt(0).toUpperCase() ?? '');
          defaultStore.useGravatar = false;
          console.log('No Gravatar image found for', email);
        }
      } catch (error) {
        gravatarUrl = email.charAt(0).toUpperCase();
        defaultStore.useGravatar = false;
        console.error(error);
      }
    }
  }

  if (!config.dev) {
    OpenAPI.BASE = 'api';
    console.log('Backend URL: ' + OpenAPI.BASE);
  }

  console.log('Logged in as ' + uuid);
  api.defaults.headers.common['userName'] = uuid;
  defaultStore.username = uuid;
  defaultStore.gravatarUrl = gravatarUrl;
  defaultStore.cluster = publicConfig.clusterUrl;
  OpenAPI.HEADERS = { ...((OpenAPI.HEADERS as object) ?? {}), userName: uuid };
}
