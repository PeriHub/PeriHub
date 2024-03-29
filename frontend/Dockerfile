# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

# develop stage
FROM node:lts-alpine as develop-stage
WORKDIR /app
COPY app/package*.json ./
COPY app/. .

# build stage
FROM develop-stage as build-stage

ARG TRIAL
ENV TRIAL $TRIAL
ARG KEYCLOAK_URL
ENV KEYCLOAK_URL $KEYCLOAK_URL
ARG REALM
ENV REALM $REALM
ARG CLIENT_ID
ENV CLIENT_ID $CLIENT_ID

RUN npm i -g @quasar/cli
RUN npm install
RUN quasar build

# production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]