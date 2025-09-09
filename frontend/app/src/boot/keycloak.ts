import Keycloak from 'keycloak-js';
import { api } from 'boot/axios';
import { OpenAPI } from '../client';
import { jwtDecode } from 'jwt-decode';
import { useDefaultStore } from 'src/stores/default-store';

export default async ({ app }) => {
  let uuid = 'user';
  let gravatarUrl = 'US';
  const store = useDefaultStore();

  console.log(process.env.KEYCLOAK_URL);
  console.log(process.env.REALM);
  console.log(process.env.CLIENT_ID);
  if (
    process.env.KEYCLOAK_URL == null ||
    process.env.KEYCLOAK_URL == '' ||
    process.env.KEYCLOAK_URL == 'KEYCLOAK_URL_VALUE'
  ) {
    if (process.env.TRIAL == 'True') {
      console.log(`I'm on a trial build`);
      let reqOptions = {
        url: 'https://randomuser.me/api',
      };
      axios.request(reqOptions).then((response) => {
        uuid = response.data.results[0].login.uuid;
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
      await keycloak.init({
        onLoad: 'login-required',
      });
      app.config.globalProperties.$keycloak = keycloak;
      // api.defaults.headers.common['Authorization'] = 'Bearer ' + keycloak.token;
      // OpenAPI.TOKEN = keycloak.token;
      const decoded = jwtDecode(keycloak.token);
      const sha256 = require('js-sha256');
      uuid = decoded.preferred_username;
      const emailHash = sha256(decoded.email);
      gravatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=404`;
      fetch(gravatarUrl)
        .then((response) => {
          if (response.ok) {
            store.useGravatar = true;
            console.log('Gravatar image found for', decoded.email);
          } else {
            const emailParts = decoded.email.split('.');
            gravatarUrl =
              emailParts[0].charAt(0).toUpperCase() +
              emailParts[1].charAt(0).toUpperCase();
            store.useGravatar = false;
            console.log('No Gravatar image found for', decoded.email);
          }
        })
        .catch((error) => {
          gravatarUrl = decoded.email.charAt(0).toUpperCase();
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
  store.cluster = process.env.CLUSTER_URL;
  OpenAPI.HEADERS = {
    userName: uuid,
  };
};
