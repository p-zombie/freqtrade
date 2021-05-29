Creating the app
```shell
git clone https://github.com/joaorafaelm/freqtrade.git && cd freqtrade
heroku update beta
heroku plugins:install @heroku-cli/plugin-manifest
heroku create --manifest
heroku labs:enable runtime-dyno-metadata
heroku addons:create securekey
heroku dyno:scale web=1
```

Set environment variables
```
# example: heroku config:set KEY=value
TELEGRAM_TOKEN_LIVE=bot token
TELEGRAM_CHAT_ID_LIVE=chat id
TELEGRAM_TOKEN_DRY=bot token for dry run
TELEGRAM_CHAT_ID_DRY=
EXCHANGE_NAME=binance
EXCHANGE_KEY=your key
EXCHANGE_SECRET=your secret
LIVE_STRATEGY=SMAOffsetV2
DRY_STRATEGY=CombinedBinHAndClucV8
# UI credentials
USERNAME=admin
PASSWORD=admin
```

Deploying
```
git push heroku master
```

Open [FreqUI](https://github.com/freqtrade/frequi)
```
heroku open
```

Edit `Procfile` to add or remove bots.
