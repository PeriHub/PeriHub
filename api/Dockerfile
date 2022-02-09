FROM openjdk:slim
COPY --from=python:3.7 / /

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL

RUN pip install fastapi uvicorn matplotlib scipy numpy pandas paramiko aiofiles python-multipart pyjwt requests zipfile2 

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

WORKDIR /app/

EXPOSE 80

COPY ./app /app

RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

RUN chmod +x /app/support/read.sh

CMD ["uvicorn", "apiMain:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]