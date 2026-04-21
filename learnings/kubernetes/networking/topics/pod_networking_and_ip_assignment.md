# Topic: Pod Networking and IP Assignment

## Two distinct IPs per pod

Every running pod has two IPs in play:

| Field | Example | What it is |
|---|---|---|
| `status.hostIP` | `10.0.5.23` | The EC2 instance (worker node) the pod runs on |
| `status.podIP` | `10.244.3.17` | The pod's own virtual IP, unique across the cluster |

These are different. A single EC2 instance hosts many pods, each with its own unique IP.

## How pod IPs are isolated

Each pod gets its own **Linux network namespace** — a kernel feature that gives the pod an isolated set of network interfaces, routing tables, and IP addresses, separate from the host and other pods.

Setup per pod:
1. Container runtime calls `unshare(CLONE_NEWNET)` — creates a new network namespace
2. A **veth pair** (virtual ethernet cable) is created — two virtual interfaces linked together
3. One end goes inside the pod's network namespace, assigned the pod IP (e.g. `10.244.3.17`)
4. The other end stays on the host, connected to a bridge or routing rule
5. The CNI plugin allocates the IP from a pool and sets up routing so other nodes can reach this pod

## CNI plugins

The CNI (Container Network Interface) is a plugin that runs on each node and handles IP allocation and routing setup.

**AWS VPC CNI:** Pod IPs are real secondary IPs on the EC2 instance's ENI (Elastic Network Interface). Other machines in the VPC can route to pod IPs directly without encapsulation.

**Calico / Flannel (overlay):** Pod IPs exist only within a virtual network. Traffic to `10.244.3.17` from another node gets VXLAN-encapsulated — wrapped inside a UDP packet addressed to the node's real IP, then unwrapped at the destination.

## Can two pods have the same IP?

No. Pod IPs are unique cluster-wide. The CNI plugin ensures this by allocating from non-overlapping per-node CIDR blocks (e.g. node 1 gets `10.244.1.0/24`, node 2 gets `10.244.2.0/24`).

## Why kubelet needs both IPs

- **hostIP** → API server connects to `10.0.5.23:10250` to reach kubelet
- **podIP** → kubelet connects to `10.244.3.17:2746` to reach the pod's listening socket

## Related questions

- [How does kubectl port-forward work end to end?](../questions/how_does_kubectl_port_forward_work_end_to_end.md)
