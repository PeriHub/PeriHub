// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import type Keycloak from 'keycloak-js';

class AuthStore {
  authenticated = $state(false);
  keycloak: Keycloak | null = null;

  get isAuthenticated() {
    return this.authenticated;
  }

  async login() {
    if (!this.keycloak) return;
    try {
      const authenticated = await this.keycloak.login();
      this.authenticated = Boolean(authenticated);
    } catch (error) {
      console.error('Login error:', error);
    }
  }

  async logout() {
    if (!this.keycloak) return;
    try {
      await this.keycloak.logout();
      this.authenticated = false;
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
}

export const authStore = new AuthStore();
