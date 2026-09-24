#!/bin/sh
# The frontend used to have TRIAL/CLUSTER_URL/KEYCLOAK_URL/REALM/CLIENT_ID
# baked into the built JS as literal `..._VALUE` placeholders, substituted
# here at container startup with sed. That's gone: the frontend now fetches
# these from the backend's GET /config/public at page load instead (see
# src/lib/config.ts), so the built bundle is the same regardless of
# deployment and there's nothing left for this script to substitute.
echo "Starting Nginx"
nginx -g 'daemon off;'

