FROM freqtradeorg/freqtrade:develop

USER root
RUN apt-get install gettext-base

USER ftuser
COPY requirements.txt /freqtrade/requirements.txt
RUN pip install --user -r /freqtrade/requirements.txt

COPY run.sh /freqtrade/run.sh
COPY Procfile /freqtrade/Procfile
COPY user_data /freqtrade/user_data

ENTRYPOINT ["./load_env.sh"]
