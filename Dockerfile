FROM freqtradeorg/freqtrade:develop_plot

ENV PYTHONWARNINGS="ignore"
USER root
RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install gettext-base nodejs

USER ftuser
COPY requirements.txt /freqtrade/requirements.txt
RUN pip install --user -r /freqtrade/requirements.txt
RUN jupyter labextension install jupyterlab-plotly
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget

COPY load_env.sh /freqtrade/load_env.sh
COPY Procfile /freqtrade/Procfile
COPY user_data /freqtrade/user_data

ENTRYPOINT ["./load_env.sh"]
