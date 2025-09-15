.PHONY: build-all push-all build-generator build-sentiment build-credit push-generator push-sentiment push-credit

# Simple Docker builds for host architecture (arm64 if you build on Apple Silicon or arm runners)
# Usage:
#   make build-all REG=avy1013 TAG=latest
#   make push-all REG=avy1013 TAG=latest

REG ?= avy1013
TAG ?= latest

IMG_GENERATOR := $(REG)/generator-app:$(TAG)
IMG_SENTIMENT := $(REG)/sentiment-app:$(TAG)
IMG_CREDIT := $(REG)/credit-service:$(TAG)

all: build-all push-all

build-all: build-generator build-sentiment build-credit

build-generator:
	docker build -t $(IMG_GENERATOR) apps/model_generator

build-sentiment:
	docker build -t $(IMG_SENTIMENT) apps/model_sentiment

build-credit:
	docker build -t $(IMG_CREDIT) apps/credit_service

push-all: push-generator push-sentiment push-credit

push-generator:
	docker push $(IMG_GENERATOR)

push-sentiment:
	docker push $(IMG_SENTIMENT)

push-credit:
	docker push $(IMG_CREDIT)
