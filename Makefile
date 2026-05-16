.PHONY: test build run api-run mobile-start

test:
	python -m pytest tests/

build:
	npm run build

run:
	python -m enki_ai.agents.server

api-run:
	python -m enki_ai.api.web_server

mobile-start:
	cd mobile && npm start
