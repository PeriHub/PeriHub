#!/bin/sh
# @see https://stackoverflow.com/questions/18185305/storing-bash-output-into-a-variable-using-eval
ROOT_DIR=/usr/share/nginx/html
          
# Replace env vars in JavaScript files
echo "Replacing env constants in JS"

keys="TRIAL
CLUSTER_URL
KEYCLOAK_URL
REALM
CLIENT_ID"

for file in $ROOT_DIR/js/*.js* ;
do
  echo "Processing $file ...";
  for key in $keys
  do
    value=$(eval echo \$$key)
    # echo "replace $key by $value"
    sed -i 's|'$key'|'$value'|g' $file
  done
done

echo "Starting Nginx"
nginx -g 'daemon off;'
