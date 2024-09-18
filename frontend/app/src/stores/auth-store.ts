import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    authenticated: false,
  }),
  getters: {
    isAuthenticated: (state) => state.authenticated,
  },
  actions: {
    async login() {
      try {
        const authenticated = await this.$keycloak.login();
        this.authenticated = authenticated;
      } catch (error) {
        console.error("Login error:", error);
      }
    },
    async logout() {
      try {
        await this.$keycloak.logout();
        this.authenticated = false;
      } catch (error) {
        console.error("Logout error:", error);
      }
    },
  },
});
