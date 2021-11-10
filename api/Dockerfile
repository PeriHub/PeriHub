FROM openjdk:slim
COPY --from=python:3.7 / /

RUN pip install fastapi uvicorn matplotlib scipy numpy pandas paramiko aiofiles pyevtk python-multipart meshio[all]
# pysftp 


RUN if [ "$EXTERNAL" = "False" ]; then \
        mkdir -p /root/.ssh && \
        chmod 0700 /root/.ssh && \
        ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts && \
        ssh-keyscan cara.dlr.de >> /root/.ssh/known_hosts; \
    fi
# RUN mkdir -p /root/.ssh && \
#     chmod 0700 /root/.ssh && \
#     ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts && \
#     ssh-keyscan cara.dlr.de >> /root/.ssh/known_hosts

# COPY id_rsa_cara /app/id_rsa_cara
# COPY id_rsa_cluster /app/id_rsa_cluster


WORKDIR /app/

EXPOSE 80

COPY ./app /app

RUN if [ "$EXTERNAL" = "False" ]; then chmod 600 /app/id_rsa_cara; fi
RUN if [ "$EXTERNAL" = "False" ]; then chmod 600 /app/id_rsa_cluster; fi

RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

RUN chmod +x /app/support/read.sh

CMD ["uvicorn", "apiMain:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]