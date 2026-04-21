# Topic: Kubelet Role and Responsibilities

## What it is

`kubelet` is a Go binary that runs on every **worker node** in a Kubernetes cluster. It's the node-level agent. It listens on port `10250`.

## What kubelet does

1. **Watches the API server** for pods assigned to its node
2. **Creates pods** by calling the container runtime (containerd/docker) to pull images and start containers
3. **Manages pod lifecycle** — restarts containers on failure, enforces resource limits, runs health probes
4. **Reports node and pod status** back to the API server (CPU usage, memory, pod phase)
5. **Executes API server requests** for in-cluster operations like `exec`, `logs`, and `port-forward`

## Role in port-forward

When the API server receives a port-forward request, it connects to the kubelet at `hostIP:10250` and says: "open a connection to pod X on port 2746." The kubelet:

1. Receives the request
2. Calls `connect(podIP, 2746)` — a TCP syscall to the pod's network namespace
3. Becomes a relay: reads from the API server connection, writes to the pod, and vice versa

Kubelet can reach the pod directly because it runs on the **same EC2 instance** as the pod. The pod IP (`10.244.3.17`) is a virtual IP on the host's own network, reachable via the veth pair set up by the CNI plugin.

## Role in exec

For `kubectl exec`, kubelet does something different: instead of connecting to a TCP port, it calls into the container runtime to **spawn a new process** inside the container's namespaces (PID, network, mount, etc.) and streams that process's stdin/stdout/stderr back to the API server.

## Kubelet vs kube-apiserver

| | kube-apiserver | kubelet |
|---|---|---|
| Runs on | Control plane node(s) | Every worker node |
| Listens on | 443 | 10250 |
| Role | Cluster brain, state machine, auth | Node agent, pod executor |
| Talks to | etcd, kubelet, kubectl | API server, container runtime |

## Related questions

- [How does kubectl port-forward work end to end?](../questions/how_does_kubectl_port_forward_work_end_to_end.md)
