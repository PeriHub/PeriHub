# Config unification — one source of truth, backend-driven

> **Update:** the Keycloak-specific login path this doc originally
> describes (`src/lib/auth/keycloak.ts`, the `keycloak` field in
> `GET /config/public`, `KEYCLOAK_URL`/`REALM`/`CLIENT_ID`) has since been
> removed in favour of using the generic OAuth2/OIDC path
> (`src/lib/auth/oauth.ts`, `OAUTH_*` env vars) for every IdP, Keycloak
> included - a self-hosted Keycloak realm publishes a standard OIDC
> discovery document like any other IdP, so a separate code path for it
> wasn't needed. The rest of this doc is left as-is for history; see
> `routers/config.py` and `src/lib/config.ts` for the current shape of
> `GET /config/public` (just `oauth_enabled` now, no `keycloak` field).

Removes the frontend's duplicated `VITE_TRIAL` / `VITE_CLUSTER_URL` /
`VITE_KEYCLOAK_URL` / `VITE_REALM` / `VITE_CLIENT_ID` env vars and the
`entrypoint.sh` sed-substitution mechanism that filled them in at container
startup. The frontend now fetches these from the backend at page load
instead.

## What changed

- **`backend/app/routers/config.py`** (new) — `GET /config/public`, returns
  `{deployment_mode, trial, cluster_url, keycloak, oauth_enabled}`.
  Unauthenticated (it's deployment config, not secrets - no client secret is
  ever included). Keycloak is only included if it's both configured _and_
  currently licensed (`entitlements.has_feature("keycloak_login")`), so a
  community/trial deployment never gets a Keycloak login screen even if
  `KEYCLOAK_URL` happens to be set in its `.env`.
- **`src/lib/config.ts`** — `config` now only holds genuine build/dev-time
  concerns (`dev`, `apiBase`). Everything else moved to `publicConfig`
  (safe empty defaults) + `loadPublicConfig()`, which fetches
  `GET /config/public` once at startup.
- **`src/routes/+layout.svelte`** — `onMount` now awaits `loadPublicConfig()`
  before `initialiseStore()`/`initAuth()` read `publicConfig`.
- **`src/lib/auth/keycloak.ts`** — reads `publicConfig.*` instead of
  `config.*`. Also fixes a pre-existing bug while touching this file: trial
  identity used to come from a third-party API (`https://randomuser.me/api`)
  instead of the backend; it now calls `POST /auth/trial-id` (added in the
  Phase 1 patch) instead - one less external dependency, and ties trial
  identity generation to the same backend that already tracks it.
- **`src/lib/stores/default-store.svelte.ts`** — reads `publicConfig.trial`.
- **`entrypoint.sh`** — the sed-substitution loop is gone; it just starts
  nginx now, since the built JS has no more `..._VALUE` placeholders to
  replace.
- **`.env.example` / `.env.local.example`** — updated comments; `TRIAL`,
  `CLUSTER_URL`, `KEYCLOAK_URL`, `REALM`, `CLIENT_ID` are now read by both
  containers from the one `.env`, set once.

## Verified

- `GET /config/public` tested directly: returns `trial: false, keycloak: null`
  with nothing configured; with `KEYCLOAK_URL`/`REALM`/`CLIENT_ID` set but
  the license only granting a `community` plan, `keycloak` stays `null`
  (gated correctly); with the license mocked to `enterprise` +
  `keycloak_login`, the field populates with the right values
- Ran `svelte-check` — zero new errors introduced (the 20 pre-existing
  errors are all in unrelated files - `ExpansionComp.svelte`,
  `ResultsView.svelte`, etc. - and none touch any file this patch changed)
- Ran the actual production build (`npm run build`) — succeeds
- Grepped the built output: no leftover `TRIAL_VALUE`/`KEYCLOAK_URL_VALUE`/etc.
  placeholders, no `randomuser.me` reference, and `/config/public` is
  present in the bundle where expected

## Apply on top of

Phase 1 (needs `POST /auth/trial-id` and `support/entitlements.has_feature`)
and Phase 0 (`support/globals.py`'s `deployment_mode`/Keycloak vars). If
applying this patch alone without those, `POST /auth/trial-id` won't exist
yet — trial mode will just silently fail to get a random identity (falls
back to the literal `"user"` default) until Phase 1 is also applied.

## Not changed

- `config.dev` and `config.apiBase` stay as build-time/dev concerns - there
  was no duplication to remove there.
- `entitlements`/`license_client` themselves are untouched; this patch only
  adds a read of `has_feature()` from the new config router.
