#!/bin/bash

export PATH="/home/ftuser/.local/bin:$PATH"
echo $PYTHONPATH

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

python -c "import site; print(site.USER_BASE)"
python -m site --user-base

/home/ftuser/.local/bin/honcho start
