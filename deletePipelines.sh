#!/bin/sh
set -e

GITLAB_URL="https://gitlab.dlr.de"
TOKEN=$1
PROJECT="16016"
# How many to delete from the oldest.
PER_PAGE=100
UPDATED_BEFORE=2021-11-29T15:45:00Z

echo "The following pipelines will be deleted: "
for PIPELINE in $(curl -s --header "PRIVATE-TOKEN: $TOKEN" "$GITLAB_URL/api/v4/projects/$PROJECT/pipelines?per_page=$PER_PAGE&sort=asc&updated_before=$UPDATED_BEFORE" | jq '.[].id') ; do
    echo "$PIPELINE"
done

read -p "Do you want to continue? [y/n] " choice
case "$choice" in 
  y|Y ) 
    for PIPELINE in $(curl -s --header "PRIVATE-TOKEN: $TOKEN" "$GITLAB_URL/api/v4/projects/$PROJECT/pipelines?per_page=$PER_PAGE&sort=asc&updated_before=$UPDATED_BEFORE" | jq '.[].id') ; do
        echo "Deleting pipeline $PIPELINE"
        curl --header "PRIVATE-TOKEN: $TOKEN" --request "DELETE" "https://gitlab.dlr.de/api/v4/projects/$PROJECT/pipelines/$PIPELINE"
    done;;
  n|N ) echo "no";;
  * ) echo "invalid";;
esac

# read -p "Do you want to continue? [Y/n] " -n 1 -r
# echo    # (optional) move to a new line
# if [[ $REPLY =~ ^[Yy]$ ]]
# then
#     for PIPELINE in $(curl -s --header "PRIVATE-TOKEN: $TOKEN" "$GITLAB_URL/api/v4/projects/$PROJECT/pipelines?per_page=$PER_PAGE&sort=asc&updated_before=$UPDATED_BEFORE" | jq '.[].id') ; do
#         echo "Deleting pipeline $PIPELINE"
#         curl --header "PRIVATE-TOKEN: $TOKEN" --request "DELETE" "https://gitlab.dlr.de/api/v4/projects/$PROJECT/pipelines/$PIPELINE"
#     done
# fi
