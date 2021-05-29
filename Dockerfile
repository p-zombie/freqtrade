FROM freqtradeorg/freqtrade:develop

USER root
RUN apt-get install gettext-base
RUN pip install honcho

USER ftuser

COPY run.sh /freqtrade/
COPY Procfile /freqtrade/
COPY user_data /freqtrade/user_data

ENTRYPOINT ./run.sh
