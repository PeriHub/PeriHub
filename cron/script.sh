#!/bin/sh
echo "$(date): "
curl -X 'DELETE' 'periHubApi/deleteUserData?check_date=true&days=7'
curl -X 'POST' 'trame/closeTrameInstance?port=1&cron=true'
