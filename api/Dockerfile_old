# FROM openjdk:slim
# COPY --from=python:3.9 / /
FROM  continuumio/miniconda3

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG DEV
ENV DEV $DEV

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL

ARG SMETANA
ENV SMETANA $SMETANA

ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

RUN apt-get update --allow-insecure-repositories
# RUN apt-get install libglapi-mesa

COPY requirements.txt requirements.txt
RUN if [ "$SMETANA" = "False" ]; then pip install -r requirements.txt && pip install fa-pyutils --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/4593/packages/pypi/simple ; fi


RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

# COPY id_rsa_cara /root/.ssh/id_rsa

WORKDIR /app/

EXPOSE 80

# COPY ./app /app
COPY ./app/guides /app/guides
COPY ./app/models /app/models
COPY ./app/Publications /app/Publications
COPY ./app/support /app/support
COPY ./app/api_main.py /app/api_main.py

RUN if [ "$DEV" = "True" ]; then echo "DEV=True" > .env; fi
RUN if [ "$SMETANA" = "True" ]; then echo "SMETANA=True" > .env; fi

# RUN if [ "$DEV" = "True" ]; then echo "DEV"; fi
# RUN if [ "$SMETANA" = "True" ]; then echo "smetana"; fi

# COPY setup.sh /app/setup.sh

# RUN chmod +x /app/setup.sh
RUN chmod +x /app/support/read.sh

# RUN conda init bash
# RUN conda activate app

# RUN ./setup.sh

COPY environment.yaml environment.yaml

RUN if [ "$SMETANA" = "True" ]; then conda update --name base conda &&\
    conda env create --file environment.yaml &&\
    conda install --name app -c dlr-sc pythonocc-core=0.17.3 &&\
    conda run -n app pip install fa-pyutils --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/4593/packages/pypi/simple &&\
    conda install conda-build &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/composite-companion/backend/smetana.git /app/support/smetana &&\
    conda develop /app/support/smetana/src/ -n app &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/composite-companion/backend/stepp.git /app/support/stepp &&\
    conda develop /app/support/stepp/src/ -n app &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/vampire.git /app/support/vampire &&\
    conda develop /app/support/vampire/src/ -n app; fi
 
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host 129.247.54.37\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi
RUN if [ "$EXTERNAL" = "False" ]; then echo "Host cara.dlr.de\n\tStrictHostKeyChecking no\n" > /root/.ssh/config; fi

# ENTRYPOINT ["tail", "-f", "/dev/null"]
CMD if [ "$SMETANA" = "True" ]; then conda run -n app --no-capture-output uvicorn api_main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips='*' --reload --reload-dir /app; else uvicorn api_main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips='*' --reload --reload-dir /app; fi
# CMD ["/bin/sh", "-c", "conda run -n app --no-capture-output uvicorn api_main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips='*' --reload --reload-dir /app"]
# CMD ["conda", "run", "--name", "app", "uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]
# CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips='*'", "--reload", "--reload-dir", "/app"]