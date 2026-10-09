// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { publicConfig, config, loadPublicConfig } from '$lib/config';
import { api } from '$lib/api/client';
import { OpenAPI } from '$lib/client';
import { defaultStore } from '$lib/stores/default-store.svelte';
import { authStore } from '$lib/stores/auth-store.svelte';
import { isPublicPath } from '$lib/utils/public-routes';

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

// A page's onMount runs before the root layout's, so generated-client calls made on mount would
// otherwise go out before initAuth() has attached the session header - and the backend
// would answer as the anonymous "user". Every generated-client request waits for initAuth() instead.
const authHeaders: Record<string, string> = {};
let markAuthReady = () => {};
const authReady = new Promise<void>((resolve) => (markAuthReady = resolve));

/** The auth headers, once initAuth() has finished - for requests made outside the generated client. */
export const getAuthHeaders = () => authReady.then(() => authHeaders);

OpenAPI.HEADERS = getAuthHeaders;

function browser() {
  return typeof window !== 'undefined';
}

/** Attaches the PeriHub session token as a Bearer token to every request. */
function applySessionToken(token: string) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  authHeaders.Authorization = `Bearer ${token}`;
}

/** Validates `token` via /auth/me; on success marks the store authenticated, else forgets the token. */
async function loadProfile(token: string): Promise<MeResponse | null> {
  applySessionToken(token);
  try {
    const response = await api.get<MeResponse>('/auth/me');
    authStore.authenticated = true;
    authStore.role = response.data.role;
    return response.data;
  } catch (e) {
    console.log('Session token is no longer valid:', e);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    return null;
  }
}

/** Leaves a guest session for a real login: the IdP with OAuth, the login page otherwise. */
export async function leaveGuestSession(): Promise<void> {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  if (publicConfig.oauthEnabled) await redirectToLogin();
  else window.location.href = '/auth/login';
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
 * - a stored session token that's still valid via GET /auth/me wins,
 *   regardless of deployment mode
 * - otherwise, if guest access is on, ask the backend for a throwaway
 *   guest account (POST /auth/guest) instead of a login
 * - otherwise, redirect to the IdP if OAuth is configured, or send the
 *   browser to /auth/login (local email/password) if it isn't - except on
 *   public pages (utils/public-routes.ts), which anonymous visitors may browse
 */
export async function initAuth() {
  try {
    await setUpAuth();
  } finally {
    // Also on failure or a login redirect, so requests never hang on it.
    markAuthReady();
  }
}

async function setUpAuth() {
  await loadPublicConfig();

  let uuid = 'user';
  let gravatarUrl = 'US';

  console.log(
    publicConfig.oauthEnabled ? 'Using OAuth/OIDC login' : 'Using local email/password login'
  );
  const storedToken = browser() ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;
  let profile = storedToken ? await loadProfile(storedToken) : null;

  // Guest access: visitors without a session get a throwaway guest account instead of a login.
  if (!profile && publicConfig.guestAccess) {
    try {
      const response = await api.post<LocalAuthResponse>('/auth/guest');
      localStorage.setItem(TOKEN_STORAGE_KEY, response.data.token);
      profile = await loadProfile(response.data.token);
    } catch (e) {
      console.error('Failed to create a guest session:', e);
    }
  }

  if (!profile) {
    // Public pages (home, Models/Materials teasers, legal pages) stay browsable without a login.
    if (browser() && isPublicPath(window.location.pathname)) return;
    if (publicConfig.oauthEnabled) {
      try {
        await redirectToLogin();
      } catch (error) {
        console.error('Failed to start OAuth login:', error);
      }
    } else if (browser()) {
      window.location.href = '/auth/login';
    }
    return; // either the browser is navigating away, or login couldn't be started
  }

  uuid = profile.display_name;

  // crypto.subtle only exists in secure contexts (https/localhost) - skip Gravatar otherwise.
  if (profile.email && crypto.subtle) {
    const email = profile.email;
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(email));
    const emailHash = Array.from(new Uint8Array(digest), (b) =>
      b.toString(16).padStart(2, '0')
    ).join('');
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

  if (!config.dev) {
    OpenAPI.BASE = 'api';
    console.log('Backend URL: ' + OpenAPI.BASE);
  }

  console.log('Logged in as ' + uuid);
  defaultStore.username = uuid;
  defaultStore.gravatarUrl = gravatarUrl;
}
