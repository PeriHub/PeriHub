FROM python:3.9
LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

RUN apt-get update --allow-insecure-repositories &&\
    apt-get install libglapi-mesa

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/

EXPOSE 80

COPY ./app/support /app/support
COPY ./app/main.py /app/main.py
COPY ./app/venv.py /app/venv.py
COPY ./app/api_main.py ./app/.env* /app


RUN virtualenv pvenv
RUN . pvenv/bin/activate && pip install trame

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]