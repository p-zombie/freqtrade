.PHONY: run
.ONESHELL:

-include .env
export

all: help

help: # show all commands
	@sed -n 's/:.#/:/p' makefile | grep -v sed

update: # update and build local image
	docker compose pull && docker compose build

pairs: # pull pairs for $COIN
	docker compose run --rm freqtrade list-pairs --config user_data/config.test.json --quot=$(COIN) --print-json

data: # download data
	docker compose run --rm freqtrade download-data --config user_data/config.test.json --days 30

test: # run backtest
	docker compose run --rm freqtrade backtesting --config user_data/config.test.json --strategy-list $(STRATEGY) --ticker-interval=$(INTERVAL)

build: # build app
	docker compose build

stop: # stop containers
	docker compose stop

logs: # tail logs for $APP
	heroku logs --tail --app $(APP)

output: # build output
	heroku builds:output --app $(APP)
