FROM openjdk:slim
COPY --from=python:3.7 / /

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL
ARG FASERVICES
ENV FASERVICES $FASERVICES

RUN pip install fastapi uvicorn matplotlib scipy numpy pandas paramiko aiofiles python-multipart 
#requests 
# meshio[all]
# pysftp 
#pyevtk 


# RUN if [ "$EXTERNAL" = "False" ]; then \
#         mkdir -p /root/.ssh && \
#         chmod 0700 /root/.ssh && \
#         ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts && \
#         ssh-keyscan cara.dlr.de >> /root/.ssh/known_hosts; \
#     fi
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh
#     ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts && \
#     ssh-keyscan cara.dlr.de >> /root/.ssh/known_hosts

# RUN cp /app/certs/id_rsa_cara /app/id_rsa_cara
# RUN cp /app/certs/id_rsa_cluster /app/id_rsa_cluster

WORKDIR /app/

EXPOSE 80

COPY ./app /app

# RUN if [ "$EXTERNAL" = "False" ]; then chmod 600 /app/certs/id_rsa_cara; fi
# RUN if [ "$EXTERNAL" = "False" ]; then chmod 600 /app/certs/id_rsa_cluster; fi

RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

RUN chmod +x /app/support/read.sh

RUN bash -c "if [ "$FASERVICES" = "True" ] ; then echo uvicorn apiMain:app --host 0.0.0.0 --port 80 --ssl-certfile /app/certs/jenkins.pem --proxy-headers --forwarded-allow-ips='*' --reload --reload-dir /app > run.sh; else echo uvicorn apiMain:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips='*' --reload --reload-dir /app > run.sh; fi; chmod 777 run.sh;"
CMD ./run.sh

#CMD ["uvicorn", "apiMain:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]