# develop stage
FROM node:lts-alpine as develop-stage
WORKDIR /app
COPY app/package*.json ./
COPY app/. .

# build stage
FROM develop-stage as build-stage
RUN npm i -g @quasar/cli
RUN npm install
RUN quasar build

# production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]