.PHONY: run
.ONESHELL:

-include .env
export

STRATEGIES = $(shell ls user_data/strategies | sed "s/.py//g" | tr "\n" " ")
TODAY = $(shell date +'%Y-%m-%d')
all: help

help: # show all commands
	@sed -n 's/:.#/:/p' makefile | grep -v sed

build: # update and build local image
	docker compose pull && docker compose build

pairs: # pull pairs for $COIN
	docker compose run --rm freqtrade \
		freqtrade list-pairs --config test.json --quot=$(COIN) --print-json

list-data: # list data
	docker compose run --rm freqtrade \
		freqtrade list-data --config test.json

list-strats: # list strategies
	@ls user_data/strategies

data: # download data
	docker compose run --rm freqtrade \
		freqtrade download-data --config test.json  --timerange $(TIMERANGE)  -t $(TIMEFRAME)

test: # run backtest
	docker compose run --rm freqtrade \
		freqtrade backtesting --config test.json --strategy-list $(STRATEGY) --timeframe $(TIMEFRAME) --timerange=$(TIMERANGE) \
		--export=trades --export-filename=/freqtrade/user_data/backtest_results/$(TODAY).json
	osascript -e 'display notification "Done"'

test-all: # run backtest on all strats
	docker compose run --rm freqtrade \
		freqtrade backtesting --config test.json --strategy-list $(STRATEGIES) --timerange=$(TIMERANGE) --timeframe $(TIMEFRAME)
	osascript -e 'display notification "Done"'

hyperopt: # run hyper opt
	docker compose run --rm freqtrade \
		freqtrade hyperopt --config test.json --hyperopt-loss $(LOSS) --spaces $(SPACES) --strategy $(STRATEGY) -e $(EPOCHS) --timerange=$(TIMERANGE) --timeframe=$(TIMEFRAME) --random-state 42
	osascript -e 'display notification "Done"'

stop: # stop containers
	docker compose stop

logs: # tail logs for $APP
	heroku logs --tail --app $(APP)

output: # build output
	heroku builds:output --app $(APP)

lab: # run jupyterlab server
	docker compose up lab
