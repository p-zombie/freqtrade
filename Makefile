update:
	docker-compose pull
		
pairs:
	docker-compose run --rm freqtrade list-pairs --quot=$(COIN) --print-json

data:
	docker-compose run --rm freqtrade download-data --exchange binance --days 5 -t 1h

test:
	docker-compose run --rm freqtrade backtesting --config user_data/config.test.json --strategy-list $(STRATEGY) --ticker-interval=$(INTERVAL)

run:
	docker-compose up -d

logs:
	docker-compose logs -f

stop:
	docker-compose stop
