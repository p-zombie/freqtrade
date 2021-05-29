#!/bin/bash

export PATH="/home/ftuser/.local/bin:$PATH"
echo $PYTHONPATH

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

ls /home/ftuser
ls /home/ftuser/.local
envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

sudo - ftuser
honcho start
