FROM openjdk:slim
COPY --from=python:3.9 / /

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG DEV
ENV DEV $DEV

ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL

RUN apt-get update --allow-insecure-repositories
RUN apt-get install libglu1-mesa -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install fa-pyutils --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/4593/packages/pypi/simple
RUN pip install exodusreader --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/26404/packages/pypi/simple
RUN pip install --upgrade git+https://github.com/dlr-wf/crackpy.git
RUN pip install shepard-client --extra-index-url https://gitlab.com/api/v4/projects/27250272/packages/pypi/simple 

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

WORKDIR /app/

EXPOSE 80

COPY ./app/guides /app/guides
COPY ./app/models /app/models
COPY ./app/Publications /app/Publications
COPY ./app/support /app/support
COPY ./app/api_main.py /app/api_main.py

RUN if [ "$DEV" = "True" ]; then echo "DEV=True" > .env; fi
RUN echo "SMETANA=True" > .env

RUN chmod +x /app/support/read.sh

RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]