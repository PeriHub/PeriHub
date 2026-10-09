// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

const TOKEN_STORAGE_KEY = 'periHubSessionToken';

/**
 * Tracks whether the current visitor is logged in via OAuth2/OIDC (see
 * $lib/auth/oauth.ts, which is what actually drives login - this store
 * just holds the resulting state for the rest of the app to read, plus
 * the one thing that's genuinely a user action: logging out).
 */
class AuthStore {
  authenticated = $state(false);
  /** Account role from /auth/me ('admin' | 'developer' | 'member' | 'viewer' | 'guest'); null only when not logged in. */
  role = $state<string | null>(null);
  /** May create/edit own models and save default configs - mirrors the backend's require_model_author. */
  canAuthorModels = $derived(this.role === 'admin' || this.role === 'developer');
  /** Anonymous guest account (guest access) - limited features, see backend support/guest.py. */
  isGuest = $derived(this.role === 'guest');
  /** A real account (not anonymous, not guest) - may use the material library and own models. */
  hasAccount = $derived(this.authenticated && !this.isGuest);
  /** Set once the root layout's initAuth() finished - before that, `authenticated` is still false for everyone. */
  ready = $state(false);

  /**
   * Clears the stored PeriHub session token and reloads the page. With
   * OAuth enabled, $lib/auth/oauth.ts's initAuth() will find no valid
   * session on the reload and redirect the browser to the IdP's login
   * page again, mirroring the previous Keycloak adapter's behaviour.
   */
  logout() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    this.authenticated = false;
    this.role = null;
    window.location.href = '/';
  }
}

export const authStore = new AuthStore();
