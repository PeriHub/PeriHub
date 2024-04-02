import Keycloak from "keycloak-js";
import { api } from "boot/axios";

const keycloakConfig = {
  url: process.env.KEYCLOAK_URL,
  realm: process.env.REALM,
  clientId: process.env.CLIENT_ID,
};

const keycloak = new Keycloak(keycloakConfig);

export default async ({ app }) => {
  if (process.env.KEYCLOAK_URL == null) {
    let uuid = "user";

    if (process.env.TRIAL == "True") {
      console.log(`I'm on a trial build`);
      if (localStorage.getItem("userName") != null) {
        api.defaults.headers.common["userName"] =
          localStorage.getItem("userName");
        return;
      } else {
        let reqOptions = {
          url: "https://randomuser.me/api",
        };
        axios.request(reqOptions).then((response) => {
          uuid = response.data.results[0].login.uuid;
        });
      }
    }
    if (process.env.DEV) {
      console.log(`I'm on a development build`);
      uuid = "dev";
    }
    console.log(uuid);
    api.defaults.headers.common["userName"] = uuid;
    localStorage.setItem("userName", uuid);
    return;
  }
  try {
    await keycloak.init({
      onLoad: "login-required",
    });
    app.config.globalProperties.$keycloak = keycloak;
    api.defaults.headers.common["Authorization"] = "Bearer " + keycloak.token;
    console.log(keycloak.token);
  } catch (error) {
    console.error("Keycloak initialization error:", error);
  }
};
