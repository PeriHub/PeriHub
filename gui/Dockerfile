# develop stage
FROM node:lts-alpine as develop-stage
WORKDIR /app
COPY app/package*.json ./
COPY app/. .

# build stage
FROM develop-stage as build-stage

ARG DEV
ENV DEV $DEV
ARG DLR
ENV DLR $DLR

RUN npm i -g @quasar/cli
RUN npm install
RUN if [ "$DLR" = "True" ]; then \
    if [ "$DEV" = "True" ]; then \
    ENV_FILE=dlr_local quasar build; \
    else \
    ENV_FILE=dlr_production quasar build; \
    fi \
    else \
    ENV_FILE=local quasar build; \
    fi

# production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]