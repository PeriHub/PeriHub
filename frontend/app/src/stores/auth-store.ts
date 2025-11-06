import { defineStore } from 'pinia';
import type Keycloak from 'keycloak-js';
import { inject } from 'vue';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    authenticated: false,
  }),
  getters: {
    isAuthenticated: (state) => state.authenticated,
  },
  actions: {
    async login() {
      const keycloak: Keycloak = inject('keycloak') as Keycloak;
      try {
        const authenticated = await keycloak.login();
        this.authenticated = authenticated;
      } catch (error) {
        console.error('Login error:', error);
      }
    },
    async logout() {
      const keycloak: Keycloak = inject('keycloak') as Keycloak;
      try {
        await keycloak.logout();
        this.authenticated = false;
      } catch (error) {
        console.error('Logout error:', error);
      }
    },
  },
});
