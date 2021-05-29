#!/bin/bash

export PATH="/home/ftuser/.local/bin:$PATH"
export PATH="/freqtrade/.local/bin:$PATH"
export PYTHONPATH=$(python -c "import site, os; print(os.path.join(site.USER_BASE, 'lib', 'python', 'site-packages'))"):$PYTHONPATH

# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

honcho start
