FROM  continuumio/miniconda3

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

RUN apt-get update --allow-insecure-repositories

COPY requirements.txt requirements.txt
COPY environment.yaml environment.yaml

RUN conda update --name base conda &&\
    conda env create --file environment.yaml &&\
    conda install --name app -c dlr-sc pythonocc-core=0.17.3 &&\
    conda run -n app pip install fa-pyutils --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/api/v4/projects/4593/packages/pypi/simple &&\
    conda install conda-build &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/composite-companion/backend/smetana.git /app/support/smetana &&\
    conda develop /app/support/smetana/src/ -n app &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/composite-companion/backend/stepp.git /app/support/stepp &&\
    conda develop /app/support/stepp/src/ -n app &&\
    git clone https://__token__:$GITLAB_TOKEN@gitlab.dlr.de/fa_sw/vampire.git /app/support/vampire &&\
    conda develop /app/support/vampire/src/ -n app