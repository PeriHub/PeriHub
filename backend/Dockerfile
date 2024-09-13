# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

# FROM openjdk:slim
# COPY --from=python:3.9 / /
FROM python:3.11-slim
LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG CLUSTER_URL
ENV CLUSTER_URL $CLUSTER_URL

RUN apt-get update --allow-insecure-repositories &&\
    apt-get install libglu1-mesa libglib2.0-0 git build-essential libcgal-dev libeigen3-dev libmagic1 -y

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/JTHesse/crackpy.git

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

WORKDIR /app/

EXPOSE 8000

COPY ./app/__init__.py /app/__init__.py
COPY ./app/assets /app/assets
COPY ./app/models /app/models
COPY ./app/Publications /app/Publications
COPY ./app/support /app/support
COPY ./app/routers /app/routers
COPY ./app/api_main.py /app/api_main.py

RUN if [ "$CLUSTER_URL" != "" ]; then echo "Host $CLUSTER_URL\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

CMD ["fastapi", "run", "api_main.py", "--port", "8000", "--root-path", "/api"]
