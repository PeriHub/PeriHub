// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import Keycloak from 'keycloak-js';
import { jwtDecode, type JwtPayload } from 'jwt-decode';
import { sha256 } from 'js-sha256';
import { config } from '$lib/config';
import { api } from '$lib/api/client';
import { OpenAPI } from '$lib/client';
import { defaultStore } from '$lib/stores/default-store.svelte';
import { authStore } from '$lib/stores/auth-store.svelte';

interface CustomJwtPayload extends JwtPayload {
  preferred_username: string;
  email: string;
}

/**
 * Sets up auth for the app. Mirrors the old boot/keycloak.ts:
 * - if Keycloak isn't configured and this is a trial build, fetch a random
 *   demo identity
 * - otherwise, initialise Keycloak (login-required) and derive a Gravatar
 * Call once from the root layout, client-side only.
 */
export async function initAuth() {
  let uuid = 'user';
  let gravatarUrl = 'US';

  const keycloakConfigured = Boolean(config.keycloakUrl) && !config.keycloakUrl.endsWith('_VALUE');

  if (!keycloakConfigured) {
    if (config.trial) {
      console.log("I'm on a trial build");
      try {
        const response = await api.request({ url: 'https://randomuser.me/api' });
        uuid = response.data.results[0].login.uuid;
      } catch (e) {
        console.error(e);
      }
    }
  } else {
    const keycloak = new Keycloak({
      url: config.keycloakUrl,
      realm: config.realm,
      clientId: config.clientId
    });
    console.log('Using Keycloak');
    authStore.keycloak = keycloak;

    try {
      await keycloak.init({ onLoad: 'login-required' }).catch(() => {
        console.log('Keycloak init failed');
      });
      authStore.authenticated = true;

      const decoded = jwtDecode<CustomJwtPayload>(String(keycloak.token));
      uuid = decoded.preferred_username;
      const email = decoded.email;
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
    } catch (error) {
      console.error('Keycloak initialization error:', error);
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
  defaultStore.cluster = config.clusterUrl;
  OpenAPI.HEADERS = { userName: uuid };
}
