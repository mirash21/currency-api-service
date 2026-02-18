.PHONY: build up down logs test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f currency-service

test:
	docker-compose exec currency-service python test_service.py

sql-demo:
	docker-compose exec currency-service python run_sql_demo.py

clean:
	docker-compose down -v
	docker system prune -f

first-run: build up logs

status:
	docker-compose ps