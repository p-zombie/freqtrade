FROM freqtradeorg/freqtrade:develop

USER root
RUN apt-get install gettext-base
RUN pip install honcho

COPY run.sh /freqtrade/
COPY Procfile /freqtrade/

USER ftuser
ENTRYPOINT ./run.sh
