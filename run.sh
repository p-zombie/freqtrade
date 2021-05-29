#!/bin/bash

export PYTHONUSERBASE="/home/ftuser/.local"

envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

honcho start
