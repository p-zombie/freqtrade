Creating the app
```shell
heroku update beta
heroku plugins:install @heroku-cli/plugin-manifest
heroku create --manifest
```

Set environment variables
```
TELEGRAM_TOKEN_LIVE=bot token
TELEGRAM_CHAT_ID_LIVE=chat id
TELEGRAM_TOKEN_DRY=bot token for dry run
TELEGRAM_CHAT_ID_DRY=
EXCHANGE_NAME=binance
EXCHANGE_KEY=your key
EXCHANGE_SECRET=your secret
LIVE_STRATEGY=SMAOffsetV2
DRY_STRATEGY=CombinedBinHAndClucV8
```

Deploying
```
git push heroku master
```
