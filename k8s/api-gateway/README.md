# Kong API Gateway Configuration

This directory contains the Kubernetes resources for configuring the Kong API Gateway.

## Setup and Deployment

The setup is a two-step process:
1.  Install Kong via Helm using the custom values file.
2.  Apply the custom API gateway configurations (ingress, plugins, consumers).

### 1. Install Kong with Helm

First, add the Kong Helm repository if you haven't already:

```sh
helm repo add kong https://charts.konghq.com
helm repo update
```

Then, install Kong using the `kong-values.yaml` file provided in this directory. This file configures a custom `nodeSelector` for the Kong pods.

```sh
helm install my-kong kong/kong \
  --namespace default \
  -f k8s/api-gateway/kong-values.yaml
```

### 2. Apply API Gateway Configurations

Once Kong is running, apply the custom resources to configure routing, authentication, and rate-limiting.

```sh
kubectl apply -f k8s/api-gateway/
```

This command will apply all the `.yaml` files in this directory.

## File Breakdown

-   `kong-values.yaml`: A Helm values file to customize the Kong installation. It's used to set the `nodeSelector` to ensure Kong pods run on specific nodes.
-   `ingress.yaml`: Defines the `Ingress` resource. This controls path-based routing, sending traffic for `/model/generator` and `/model/sentiment` to the correct backend services.
-   `plugins.yaml`: Contains `KongPlugin` resources. This is where API key authentication (`key-auth`) and rate limiting (`rate-limiting`) are enabled.
-   `consumers.yaml`: Defines `KongConsumer` resources (the users of your API) and the `Secrets` that hold their unique API keys.
