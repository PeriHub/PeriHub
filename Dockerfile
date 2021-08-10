FROM python:3.7

RUN pip install fastapi uvicorn matplotlib scipy numpy aiofiles pandas paramiko pysftp

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan 129.247.54.37 > /root/.ssh/known_hosts

COPY id_rsa_shared /root/.ssh/id_rsa

RUN chmod 600 /root/.ssh/id_rsa

RUN echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config

WORKDIR /app/

EXPOSE 80

COPY ./app /app

CMD ["uvicorn", "modelGeneratorControl:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "/app"]