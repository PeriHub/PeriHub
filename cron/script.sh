#!/bin/sh
echo "$(date): "
curl -X 'DELETE' 'periHubApi/deleteUserData?checkDate=true&days=7'
