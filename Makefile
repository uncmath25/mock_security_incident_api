.PHONY: clean build flake test start stop buuld-prod start-prod stop-prod

SHELL := /bin/bash

DEV_NAME := security-incident-api-dev
PROD_NAME := security-incident-api

default: test

clean:
	@echo "*** Cleaning repo ***"
	find . -name '__pycache__' -type d | xargs rm -rf
	find . -name '.pytest_cache' -type d | xargs rm -rf

build: clean
	@echo "*** Building development Flask docker image ***"
	docker build -f Dockerfile-dev -t uncmath25/$(DEV_NAME) .

flake: build
	@echo "*** Linting repo ***"
	docker run --rm uncmath25/$(DEV_NAME) bash -c "flake8 --ignore=E501,W503 /src"

test: flake
	@echo "*** Testing repo ***"
	docker run --rm -v "$$(pwd)/tests:/tests" uncmath25/$(DEV_NAME) bash -c "pytest /tests"

start: test
	@echo "*** Starting dockerized development flask web server ***"
	docker run --rm -d -p 9000:5000 --env-file .env.dev -v "$$(pwd)/api:/api" --name $(DEV_NAME) uncmath25/$(DEV_NAME)

stop:
	@echo "*** Stopping dockerized development flask web server ***"
	docker rm -f $(DEV_NAME)

build-prod: flake test
	@echo "*** Building production nginx uwsgi flask docker image ***"
	docker build -f Dockerfile-prod -t uncmath25/$(PROD_NAME) .

start-prod: build-prod
	@echo "*** Starting production nginx uwsgi flask docker container ***"
	docker run -d -p 9000:80 --env-file .env.prod --name $(PROD_NAME) uncmath25/$(PROD_NAME)

stop-prod:
	@echo "*** Stopping production nginx uwsgi flask docker container ***"
	docker rm -f $(PROD_NAME)
