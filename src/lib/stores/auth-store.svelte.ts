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
    window.location.href = '/';
  }
}

export const authStore = new AuthStore();
