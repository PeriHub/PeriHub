# develop stage
FROM node:lts-alpine as develop-stage

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG DEV
ENV DEV $DEV
ENV NODE_OPTIONS=--openssl-legacy-provider

WORKDIR /app

RUN if [ "$DEV" = "True" ]; then echo "VUE_APP_DEV=True" > .env; fi

COPY app/package*.json ./

RUN npm install
COPY app/. .

# # build stage
# FROM develop-stage as build-stage
RUN npm run build

# production stage
FROM nginx:alpine as production-stage
COPY --from=develop-stage /app/dist /usr/share/nginx/html

EXPOSE 90
CMD ["nginx", "-g", "daemon off;"]