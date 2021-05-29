#!/bin/bash

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

pip install --user honcho
honcho start
