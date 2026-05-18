# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

# develop stage
FROM node:24-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS prod

COPY app/package*.json ./
COPY app/pnpm-lock.yaml ./
WORKDIR /app
RUN pnpm fetch --prod

COPY app/. .
RUN npm i -g @quasar/cli
RUN npm run patch
RUN npm run build

FROM nginx:alpine as production-stage
COPY --from=prod /app/dist/spa /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#CMD ["nginx", "-g", "daemon off;"]