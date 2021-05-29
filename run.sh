#!/bin/bash

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

# honcho start
freqtrade trade --config dry.json --strategy $DRY_STRATEGY --db-url $DRY_DATABASE_URL
