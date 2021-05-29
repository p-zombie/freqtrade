#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

cat /etc/passwd
envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

honcho start -f Botfile
