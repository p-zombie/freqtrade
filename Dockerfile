# syntax = docker/dockerfile:experimental
FROM freqtradeorg/freqtrade:stable

ENV PYTHONWARNINGS="ignore"
ENV PIP_CACHE_DIR="/home/ftuser/.cache"
ENV PYTHONUSERBASE="/home/ftuser/.local"



USER root
RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install gettext-base nodejs cmake libopenmpi-dev zlib1g-dev libtinfo5

RUN --mount=type=cache,mode=0755,target=/home/ftuser/.cache pip install jupyterlab ipywidgets>=7.5 matplotlib
RUN jupyter labextension install jupyterlab-plotly
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget

COPY requirements.txt /freqtrade/requirements.txt
RUN --mount=type=cache,mode=0755,target=/home/ftuser/.cache pip install -r /freqtrade/requirements.txt

COPY requirements-rl.txt /freqtrade/requirements-rl.txt
RUN --mount=type=cache,mode=0755,target=/home/ftuser/.cache pip install -r /freqtrade/requirements-rl.txt

COPY load_env.sh /freqtrade/load_env.sh
COPY Procfile /freqtrade/Procfile
COPY user_data /freqtrade/user_data


USER ftuser
ENTRYPOINT ["./load_env.sh"]
