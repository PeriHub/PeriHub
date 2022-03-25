FROM openjdk:slim
COPY --from=python:3.7 / /

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

WORKDIR /app/

EXPOSE 80

# COPY ./app /app
COPY ./app/guides /app/guides
COPY ./app/models /app/models
COPY ./app/Publications /app/Publications
COPY ./app/support /app/support
COPY ./app/api_main.py ./app/.env* /app

RUN if [ "$DEV" = "True" ]; then echo "DEV=True" > .env; fi

RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

RUN chmod +x /app/support/read.sh

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]