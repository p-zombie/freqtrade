FROM freqtradeorg/freqtrade:develop

USER root
RUN apt-get install gettext-base

USER ftuser
RUN pip install --user --no-cache-dir honcho

COPY run.sh /freqtrade/
COPY Procfile /freqtrade/
COPY user_data /freqtrade/user_data

ENTRYPOINT ./run.sh
