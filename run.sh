#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

echo $PATH
echo $USER
whoami
ls
pip install honcho
honcho start -f Botfile
