# Default config values
: "${LIVE_STRATEGY:=SMAOffsetV2}"
: "${DRY_STRATEGY:=CombinedBinHAndClucV8}"

echo "Loading env vars"
envsubst < user_data/config.live.json > live.json
envsubst < user_data/config.dry.json > dry.json

ls
honcho start
