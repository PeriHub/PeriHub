import Keycloak from 'keycloak-js';
import { api } from 'boot/axios';
import { defineBoot } from '#q-app/wrappers';
import { OpenAPI } from '../client';
import { jwtDecode } from 'jwt-decode';
import type { JwtPayload } from 'jwt-decode';
import { useDefaultStore } from 'src/stores/default-store';
import {sha256} from 'js-sha256'

interface CustomJwtPayload extends JwtPayload {
  preferred_username: string;
  email: string;
}

export default defineBoot(({ app }) => {
  // for Options API
  app.config.globalProperties.$keycloak = Keycloak;

  let uuid = 'user';
  let gravatarUrl = 'US';
  const store = useDefaultStore();
  if (
    process.env.KEYCLOAK_URL == null ||
    process.env.REALM == null ||
    process.env.CLIENT_ID == null ||
    process.env.KEYCLOAK_URL == ''
    // process.env.KEYCLOAK_URL == 'KEYCLOAK_URL' + '_VALUE'
  ) {
    if (process.env.TRIAL == 'True') {
      console.log(`I'm on a trial build`);
      const reqOptions = {
        url: 'https://randomuser.me/api',
      };
      api
        .request(reqOptions)
        .then((response) => {
          uuid = response.data.results[0].login.uuid;
        })
        .catch((e) => {
          console.error(e);
        });
    }
  } else {
    const keycloak = new Keycloak({
      url: process.env.KEYCLOAK_URL,
      realm: process.env.REALM,
      clientId: process.env.CLIENT_ID,
    });
    console.log('Using Keycloak');

    try {
      keycloak
        .init({
          onLoad: 'login-required',
        })
        .catch(() => {
          console.log('Keycloak init failed');
        });
      app.config.globalProperties.$keycloak = keycloak;
      // api.defaults.headers.common['Authorization'] = 'Bearer ' + keycloak.token;
      // OpenAPI.TOKEN = keycloak.token;
      const decoded: CustomJwtPayload = jwtDecode(String(keycloak.token));
      // const sha256 = require('js-sha256');
      uuid = decoded.preferred_username;
      const email = decoded.email;
      const emailHash = sha256(email);
      gravatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=404`;
      fetch(gravatarUrl)
        .then((response) => {
          if (response.ok) {
            store.useGravatar = true;
            console.log('Gravatar image found for', email);
          } else {
            const emailParts = email.split('.');
            gravatarUrl =
              emailParts[0]!.charAt(0).toUpperCase() + emailParts[1]!.charAt(0).toUpperCase();
            store.useGravatar = false;
            console.log('No Gravatar image found for', email);
          }
        })
        .catch((error) => {
          gravatarUrl = email.charAt(0).toUpperCase();
          store.useGravatar = false;
          console.error(error); // Something went wrong while fetching the image
        });
    } catch (error) {
      console.error('Keycloak initialization error:', error);
    }
  }

  if (process.env.DEV) {
    console.log(`I'm on a development build`);
    // uuid = 'dev';
    // gravatarUrl = 'DEV';
    // store.useGravatar = false;
  } else {
    OpenAPI.BASE = 'api';
    console.log('Backend URL: ' + OpenAPI.BASE);
  }

  console.log('Logged in as ' + uuid);
  api.defaults.headers.common['userName'] = uuid;
  store.username = uuid;
  store.gravatarUrl = gravatarUrl;
  store.cluster = process.env.CLUSTER_URL!;
  OpenAPI.HEADERS = {
    userName: uuid,
  };
});
