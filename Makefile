.PHONY: build-all push-all build-generator build-sentiment build-credit push-generator push-sentiment push-credit deploy-all undeploy-all
.PHONY: tls-secrets create-monitoring-ns

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

deploy-all:
	kubectl apply -f k8s/credit_service/
	kubectl apply -f k8s/generator/
	kubectl apply -f k8s/sentiment/
	kubectl apply -f k8s/api-gateway/

undeploy-all:
	kubectl delete -f k8s/credit_service/
	kubectl delete -f k8s/generator/
	kubectl delete -f k8s/sentiment/
	kubectl delete -f k8s/api-gateway/

# --- TLS Utilities ---
# Generate self-signed certs and create TLS secrets for Ingress
tls-secrets: create-monitoring-ns
	mkdir -p tls
	# Generate cert for llm.local
	openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
	  -keyout tls/llm.local.key -out tls/llm.local.crt \
	  -subj "/CN=llm.local" -addext "subjectAltName=DNS:llm.local"
	# Generate cert for grafana.local
	openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
	  -keyout tls/grafana.local.key -out tls/grafana.local.crt \
	  -subj "/CN=grafana.local" -addext "subjectAltName=DNS:grafana.local"
	# Create or update TLS secrets
	kubectl -n default create secret tls llm-tls --cert=tls/llm.local.crt --key=tls/llm.local.key --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n monitoring create secret tls grafana-tls --cert=tls/grafana.local.crt --key=tls/grafana.local.key --dry-run=client -o yaml | kubectl apply -f -

# Ensure monitoring namespace exists
create-monitoring-ns:
	kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
