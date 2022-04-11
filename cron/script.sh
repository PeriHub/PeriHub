#!/bin/sh
echo "$(date): "
curl -X 'DELETE' 'periHubApi/deleteUserData?checkDate=true&days=7'
curl -X 'POST' 'trame/closeTrameInstance?port=1&cron=true'
