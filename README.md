# LLM Inference Platform 🚀

This project implements a scalable LLM (Large Language Model) inference platform on Kubernetes, designed to serve machine learning models as APIs. It includes features like API authentication, rate limiting, usage tracking with a credit system, and monitoring.

## 🛠️ Tools & Technologies

| Tool | Description | Logo |
|------|-------------|------|
| **Kubernetes** | Container orchestration platform for managing containerized applications | <img src="https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg" width="50" height="50"> |
| **Kong** | API Gateway for authentication, routing, and rate limiting | <img src="https://media.licdn.com/dms/image/v2/D4E0BAQHv7yIWJEYuMQ/company-logo_200_200/company-logo_200_200/0/1721680122463/konghq_logo?e=1761177600&v=beta&t=jrR5ityTJqZrX-XdbxzZ8poHg7RIite8nmBUGrbVWhg" width="50" height="50"> |
| **FastAPI** | Modern Python web framework for building high-performance APIs | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="50" height="50"> |
| **Prometheus** | Monitoring and alerting toolkit for collecting time-series data | <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Prometheus_software_logo.svg" width="50" height="50"> |
| **Grafana** | Analytics and monitoring platform for visualizing metrics | <img src="https://upload.wikimedia.org/wikipedia/commons/a/a1/Grafana_logo.svg" width="50" height="50"> |
| **Docker** | Platform for developing and running applications in containers | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="50" height="50"> |
| **Helm** | Kubernetes package manager for deploying applications | <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Helm-logo.svg" width="50" height="50"> |
| **Hugging Face** | Machine learning model hub and transformers library | <img src="https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.svg" width="50" height="50"> |

## ✨ Features

- **🤖 Scalable LLM Services**: Two models are deployed:
    - **📝 Text Generation**: Generates text based on a prompt.
    - **😊 Sentiment Analysis**: Analyzes the sentiment of a given text.
- **🛡️ API Gateway**: Uses Kong as an API gateway for:
    - **🔐 Authentication**: API key-based authentication for users.
    - **⏱️ Rate Limiting**: Per-user rate limiting to control usage.
    - **🛤️ Path-Based Routing**: Routes requests to the appropriate backend service.
- **💳 Usage Tracking & Credits**: A dedicated service tracks API usage and manages a credit system. Users are blocked when their credits run out.
- **📊 Monitoring**: Integrated with Prometheus and Grafana for observing:
    - Request counts and latency.
    - CPU/Memory utilization.
    - A pre-configured Grafana dashboard is included.
- **❤️ Health Checks**: Liveness and readiness probes for all services to ensure reliability.
- **🎮 GPU Scheduling**: Demonstrates scheduling workloads to nodes with GPU support (simulated).
- **🔒 Security**:
    - TLS termination at the ingress gateway.
    - Kubernetes secrets for sensitive data.
    - Hardened security contexts for containers.

## 🏗️ Architecture

The platform consists of the following components:

1.  **🌉 Kong API Gateway**: The single entry point for all API traffic. It handles authentication, rate limiting, and routing to backend services.
2.  **🤖 LLM Services**:
    - `generator-service`: A FastAPI application serving a text generation model (`distilgpt2`).
    - `sentiment-service`: A FastAPI application serving a sentiment analysis model (`distilbert-base-uncased-finetuned-sst-2-english`).
3.  **💰 Credit Service**: A FastAPI application that manages user credits using an in-memory SQLite database.
4.  **📈 Monitoring Stack**:
    - **Prometheus**: Scrapes metrics from the API gateway and other services.
    - **Grafana**: Provides a dashboard for visualizing the collected metrics.

All services are deployed on a Kubernetes cluster.

## 📁 Repository Structure

```
.
├── services                # Application source code and k8s charts
│   ├── credit
│   │   ├── src
│   │   └── chart
│   ├── generator
│   │   ├── src
│   │   └── chart
│   └── sentiment
│       ├── src
│       └── chart
├── platform                # Platform-level k8s configurations
│   ├── api-gateway
│   └── monitoring
├── tls                     # TLS certificate generation scripts/files
└── Makefile                # Makefile for common tasks
```

## 📋 Prerequisites

- `kubectl` ⚡
- A Kubernetes cluster (e.g., Minikube, Kind, or a cloud provider) ☁️
- `docker` 🐳
- `make` (optional, for convenience) 🔨
- `openssl` (for generating TLS certificates) 🔐
- `helm` (for deploying Kong and Prometheus) ⛵
- `curl` (for testing the API) 🌐

## 🚀 Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/avy-1013/LLMOps-Inference_Platform
cd LLMOps-Inference_Platform
```

### 2. Set Up Kubernetes Cluster

Ensure your Kubernetes cluster is running and `kubectl` is configured to connect to it. For this project, at least one node should be labeled for GPU workloads.

```sh
# Label one of your nodes (replace <your-node-name> with your actual node name)
kubectl label nodes <your-node-name> gpu=true
```

### 3. Deploy Monitoring Stack 📊

Deploy Prometheus and Grafana to the `monitoring` namespace.

```sh
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring -f platform/monitoring/prometheus-values.yaml
```

### 4. Deploy Kong API Gateway 🌉

Deploy Kong to the `kong` namespace.

```sh
kubectl create namespace kong
helm repo add kong https://charts.konghq.com
helm repo update
helm install kong kong/kong -n kong -f platform/api-gateway/kong_install/kong-values.yaml
```

### 5. Create TLS Secret 🔐

Generate a self-signed TLS certificate and create a Kubernetes secret.

```sh
make tls-secrets
```

### 6. Deploy Applications 🚀

Apply the Kubernetes manifests for all services.

```sh
make deploy-all
```

This will deploy the credit service, the two LLM services, and configure the ingress routes and plugins.

## 🎯 Usage

To use the API, you need an API key. The system is pre-configured with two users: `avy` and `vaibhav`.

**🔑 API Keys:**
-   `avy`: `my-secret-api-key`
-   `vaibhav`: `another-super-secret-key`

You will also need to get the external IP of the Kong proxy and add it to your `/etc/hosts` file.

```sh
# The following script automatically finds the external IP of the Kong gateway and
# maps the hostnames 'llm.local' and 'grafana.local' to it in your /etc/hosts file.
# This is crucial for accessing the services from your local machine.
# NOTE: This method works best with cloud-based Kubernetes providers. If you are using
# a local cluster like Minikube, you may need to use `minikube ip` to get the IP address.
# Wait for Kong to get an external IP
export KONG_IP=$(kubectl get svc -n kong kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
while [ -z "$KONG_IP" ]; do
  echo "Waiting for Kong external IP..."
  sleep 5
  export KONG_IP=$(kubectl get svc -n kong kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
done
echo "Kong IP: $KONG_IP"

echo "$KONG_IP llm.local" | sudo tee -a /etc/hosts
echo "$KONG_IP grafana.local" | sudo tee -a /etc/hosts
```

### 📝 Text Generation

```sh
curl -i -k -X POST https://llm.local/model/generator/generate \
  -H "apikey: my-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, world!"
  }'
```

### 😊 Sentiment Analysis

```sh
curl -i -k -X POST https://llm.local/model/sentiment/predict \
  -H "apikey: my-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love using this platform!"
  }'
```

## 📊 Monitoring

Access the Grafana dashboard to view metrics. The ingress is configured for `grafana.local`.

```sh
# Get Grafana admin password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

Open your browser to `https://grafana.local`. Log in with username `admin` and the password you retrieved. You should find a pre-configured dashboard for the LLM services.

## 🔮 Future Improvements

- **📦 Use Helm Charts**: Refactor the Kubernetes manifests in the `k8s` directory into Helm charts. This will make the deployments more manageable, configurable, and reusable. For example, a single chart could be created for the ML services, and different `values.yaml` files could be used to deploy the `generator` and `sentiment` models.
- **💾 Persistent Storage for Credit Service**: The credit service currently uses an in-memory SQLite database, which means all credit data is lost when the service restarts. For a production-like system, this should be replaced with a persistent database like PostgreSQL or MySQL.
- **🔄 CI/CD Pipeline**: Implement a CI/CD pipeline (e.g., using GitHub Actions) to automate the building, testing, and deployment of the applications. This would include steps for running tests, building Docker images, pushing them to a registry, and updating the Kubernetes deployments.
- **⚙️ Configuration Management**: Centralize configuration using a tool like Helm `values.yaml` or Kustomize, instead of hardcoding values in environment variables or Kubernetes manifests. For example, the `CREDIT_SERVICE_URL` in the application code.
- **🛡️ Enhanced Security**:
    - Use a secret management tool like HashiCorp Vault or Sealed Secrets to manage secrets more securely than plain Kubernetes Secrets.
    - Implement network policies to restrict traffic between pods.

---

## 🌟 Star This Repo!

If you found this project helpful, please give it a star! ⭐

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
