# develop stage
FROM node:lts-alpine as develop-stage

ARG FASERVICES
ENV FASERVICES $FASERVICES

RUN if [ "$FASERVICES" = "True" ]; then echo "VUE_APP_ROOT_API=http://fa-jenkins2:6020/" > /app/.env; fi

WORKDIR /app
COPY app/package*.json ./
RUN npm install
COPY app/. .

# # build stage
# FROM develop-stage as build-stage
RUN npm run build

# production stage
FROM nginx:alpine as production-stage
COPY --from=develop-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
# COPY nginx.conf.ssl* /etc/nginx/nginx.conf

EXPOSE 90
CMD ["nginx", "-g", "daemon off;"]