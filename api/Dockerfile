FROM python:3.7

RUN pip install fastapi uvicorn matplotlib scipy numpy pandas paramiko aiofiles pyevtk
# pysftp 

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts && \
    ssh-keyscan cara.dlr.de >> /root/.ssh/known_hosts

COPY id_rsa_cara /app/id_rsa_cara
COPY id_rsa_cluster /app/id_rsa_cluster

RUN chmod 600 /app/id_rsa_cara
RUN chmod 600 /app/id_rsa_cluster

RUN echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config
RUN echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config


WORKDIR /app/

EXPOSE 80

COPY ./app /app

CMD ["uvicorn", "modelGeneratorControl:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "/app"]