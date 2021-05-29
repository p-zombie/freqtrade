#!/bin/bash

export PATH="/home/ftuser/.local/bin:$PATH"
echo $PYTHONPATH

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

/home/ftuser/.local/bin/python -m honcho start
