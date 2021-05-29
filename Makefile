.PHONY: run
.ONESHELL:

-include .env
export

all: help

help: # show all commands
	@sed -n 's/:.#/:/p' makefile | grep -v sed

build: # update and build local image
	docker compose pull && docker compose build

pairs: # pull pairs for $COIN
	docker compose run --entrypoint "freqtrade" --rm freqtrade list-pairs --config user_data/config.test.json --quot=$(COIN) --print-json

list-data: # list data
	docker compose run --entrypoint "freqtrade" --rm freqtrade list-data --userdir /freqtrade/user_data

data: # download data
	docker compose run --entrypoint "freqtrade" --rm freqtrade download-data --userdir /freqtrade/user_data --config user_data/config.test.json --days $(DAYS) -t $(TIMEFRAME)

test: # run backtest
	docker compose run --entrypoint "freqtrade" --rm freqtrade backtesting --config user_data/config.test.json --userdir /freqtrade/user_data --strategy-list $(STRATEGY) -i $(TIMEFRAME)

stop: # stop containers
	docker compose stop

logs: # tail logs for $APP
	heroku logs --tail --app $(APP)

output: # build output
	heroku builds:output --app $(APP)
