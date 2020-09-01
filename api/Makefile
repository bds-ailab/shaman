.SHELL: /usr/bin/env bash

VERSION := 1.0.2

dev-environment:
	docker stack deploy -c compose/mongo.yml -c compose/dev.yml mongo-dev

test:
	pytest

lint:
	flake8

format:
	black src/ tests/

docker:
	docker build -t shaman_api:$(VERSION) -f Dockerfile .

stack:
	docker stack deploy -c compose/docker-compose.yml -c compose/mongo.yml shaman

