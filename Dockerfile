FROM freqtradeorg/freqtrade:develop

USER root
RUN apt-get install gettext-base
RUN pip install honcho

USER ftuser
COPY run.sh /freqtrade/run.sh
COPY Procfile /freqtrade/Procfile
COPY user_data /freqtrade/user_data

ENTRYPOINT ["./run.sh"]
