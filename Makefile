.PHONY: build up down migrate createsuperuser test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

front:
	cd front && npm install && npm run dev

desktop:
	cd cli && \
	( [ -d venv ] || ( command -v python3 >/dev/null 2>&1 && python3 -m venv venv || python -m venv venv ) ) && \
	( venv/bin/pip install -r requirements.txt && venv/bin/python client.py || venv/Scripts/pip install -r requirements.txt && venv/Scripts/python client.py )

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v