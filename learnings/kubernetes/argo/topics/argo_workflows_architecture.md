# Topic: Argo Workflows Architecture

## What it is

Argo Workflows is a **Kubernetes-native workflow engine** — a system for running multi-step pipelines where each step is a container (pod). It's open source software that Razorpay deploys and runs on their own clusters.

## Core components

| Component | What it does |
|---|---|
| **Workflow controller** | Watches for new Workflow CRDs, creates pods for each step, tracks completion |
| **Argo server** | HTTP API (port 2746) + Web UI for submitting and querying workflows |
| **Postgres** | Stores workflow history and status (archived workflows) |
| **MinIO** | S3-compatible object store for workflow artifacts (logs, test outputs) |

All run as pods in the `argo` namespace, kept alive permanently by Kubernetes Deployments.

## How a workflow executes

1. CI submits a Workflow YAML to the Argo API (`POST /api/v1/workflows/argo-workflows`)
2. Argo controller reads the steps and their container specs
3. For each step: controller calls Kubernetes API to create a pod
4. Pod runs the step (build, deploy, test, notify)
5. Controller watches pod status; on completion, moves to next step
6. Final step posts results back to GitHub

## Workflow as a Kubernetes CRD

Workflows are stored as **Custom Resource Definitions** in Kubernetes:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: payment-links-e2e-jtnbx
  namespace: argo-workflows
spec:
  templates:
    - name: build-image
      container:
        image: docker:latest
        command: [docker, build]
    - name: deploy-to-devstack
      container:
        image: helmfile:latest
    - name: run-e2e-tests
      container:
        image: payment-links-e2e:abc123
        command: [go, test, ./tests/e2e/...]
```

## Why it's always running

Argo is infrastructure, not a job. Like a database or message queue, it runs 24/7 waiting for submissions. The workflow controller is a reconciliation loop — it continuously watches Kubernetes for Workflow objects and ensures they progress.

## How it differs from GitHub Actions

| | GitHub Actions | Argo Workflows |
|---|---|---|
| Where it runs | GitHub's infrastructure | Your Kubernetes cluster |
| Steps are | GitHub-hosted or self-hosted runners | Kubernetes pods |
| Trigger | GitHub events (push, PR) | HTTP API call (from any CI step) |
| Visibility | GitHub UI | Argo Web UI / API |

In Razorpay's setup, GitHub Actions runs a step that **calls the Argo API** to submit a workflow. So GitHub Actions is the trigger, Argo is the executor.

## Related questions

- [What is Argo and how does it run on Kubernetes?](../questions/what_is_argo_and_how_does_it_run_on_kubernetes.md)
