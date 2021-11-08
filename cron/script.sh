#!/bin/sh
echo "$(date): "
curl -X 'POST' 'periHubApi/deleteUserData?checkDate=true&days=7'
