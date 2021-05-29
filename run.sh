#!/bin/bash

export PYTHONUSERBASE="/home/ftuser/.local"

# SQLAlchemy support
export LIVE_DATABASE_URL=${LIVE_DATABASE_URL//postgres/postgresql}
export DRY_DATABASE_URL=${DRY_DATABASE_URL//postgres/postgresql}

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

freqtrade trade --config live.json --strategy $LIVE_STRATEGY --db-url $LIVE_DATABASE_URL
