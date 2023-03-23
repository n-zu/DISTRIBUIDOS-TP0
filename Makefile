SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:

deps:
	go mod tidy
	go mod vendor

build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: up

down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: down

logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: logs

du:
	$(MAKE) down
	$(MAKE) up
.PHONY: du
