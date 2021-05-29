FROM freqtradeorg/freqtrade:develop

ENV PATH=/home/ftuser/.local/bin:$PATH
USER root
RUN apt-get install gettext-base
RUN pip install honcho

USER ftuser
RUN pip install -e . --no-cache-dir --no-build-isolation
COPY --chown=ftuser:ftuser run.sh /freqtrade/run.sh
COPY Procfile /freqtrade/Procfile
COPY user_data /freqtrade/user_data

ENTRYPOINT ["./run.sh"]
