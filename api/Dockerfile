# FROM openjdk:slim
# COPY --from=python:3.9 / /
FROM python:3.10-slim
LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG DEV
ENV DEV $DEV

# ARG GITLAB_TOKEN
# ENV GITLAB_TOKEN $GITLAB_TOKEN

ARG INTERNAL
ENV INTERNAL $INTERNAL

RUN apt-get update --allow-insecure-repositories &&\
    apt-get install libglu1-mesa libglib2.0-0 git -y

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt &&\
    pip install -i https://test.pypi.org/simple/ exodusreader &&\
    pip install -i https://test.pypi.org/simple/ gcodereader &&\
    pip install --no-cache-dir --upgrade git+https://github.com/JTHesse/crackpy.git

RUN if [ "$INTERNAL" = "True" ]; then pip install shepard-client --no-cache-dir --extra-index-url https://gitlab.com/api/v4/projects/27250272/packages/pypi/simple; fi
    # pip install gcodereader --no-cache-dir --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/26524/packages/pypi/simple &&\
    # pip install exodusreader --no-cache-dir --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/26404/packages/pypi/simple &&\

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

WORKDIR /app/

EXPOSE 80

COPY ./app/guides /app/guides
COPY ./app/assets /app/assets
COPY ./app/models /app/models
COPY ./app/Publications /app/Publications
COPY ./app/support /app/support
COPY ./app/api_main.py /app/api_main.py

RUN if [ "$DEV" = "True" ]; then echo "DEV=True" > .env; fi  &&\
    if [ "$INTERNAL" = "True" ]; then echo "INTERNAL=True" > .env; fi  &&\
    if [ "$INTERNAL" = "True" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi &&\
    if [ "$INTERNAL" = "True" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]
