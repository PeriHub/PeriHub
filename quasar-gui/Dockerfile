# develop stage
FROM node:lts-alpine as develop-stage
WORKDIR /app
COPY app/package*.json ./
COPY app/. .

# build stage
FROM develop-stage as build-stage

ARG DEV
ENV DEV $DEV

RUN npm i -g @quasar/cli
RUN npm install
RUN if [ "$DEV" = "True" ]; then ENV_FILE=local quasar build; fi
RUN if [ "$DEV" = "False" ]; then ENV_FILE=production quasar build; fi
RUN if [ "$DEV" = "" ]; then ENV_FILE=production quasar build; fi

# production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]