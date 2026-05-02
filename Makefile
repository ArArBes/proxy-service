.PHONY: build up down migrate createsuperuser test clean

all: up front

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

front:
	cd front && npm install && npm run dev

desktop:
	cd cli && pip install -r requirements.txt && python client.py

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v