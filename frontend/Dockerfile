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

RUN npm i -g @quasar/cli
RUN npm install
RUN npm run patch
RUN npm run build

# production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#CMD ["nginx", "-g", "daemon off;"]