.ONESHELL:
-include .env
export

all: help

help: # show all commands
	@sed -n 's/:.#/:/p' makefile | grep -v sed

update: # update and build local image
	docker compose pull && docker compose build
		
pairs: # pull pairs for $COIN
	docker compose run --rm freqtrade list-pairs --quot=$(COIN) --print-json

data: # download data
	docker compose run --rm freqtrade download-data --exchange binance --days 5 -t 1h

test: # run backtest
	docker compose run --rm freqtrade backtesting --config user_data/config.test.json --strategy-list $(STRATEGY) --ticker-interval=$(INTERVAL)

run: # run app
	docker compose up

stop: # stop containers
	docker compose stop

logs: # tail logs for $APP
	heroku logs --tail --app $(APP)
