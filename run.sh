#!/bin/bash

export PYTHONUSERBASE="/home/ftuser/.local"
set -a; source default.env; set +a

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

honcho start
