---
tags: [kubernetes, networking, port-forward, kubectl, kubelet, pods, vpn]
status: Answered
topics:
  - [kubectl_port_forward](../topics/kubectl_port_forward.md)
  - [pod_networking_and_ip_assignment](../topics/pod_networking_and_ip_assignment.md)
  - [kubelet_role_and_responsibilities](../topics/kubelet_role_and_responsibilities.md)
  - [vpn_split_tunnel_vs_full_tunnel](../topics/vpn_split_tunnel_vs_full_tunnel.md)
---

# How does kubectl port-forward actually work end to end?

## ❓ The Core Question

When I run `kubectl port-forward svc/argo-server -n argo 2746:2746` and then `curl localhost:2746`, how do the bytes get from my laptop to the pod? What are all the hops involved?

## 🧠 The Learning Log

### Initial Understanding

Thought port-forward was modifying routing tables or doing some network-level magic to make the pod reachable.

### 🔄 Refinement: It's just byte-copying between file descriptors, no routing changes

**My Misconception:** Port-forward alters routing tables so packets find their way to the pod.

**The Correction:** Port-forward involves 3 relay processes each holding 2 open TCP connections and copying bytes between them. No routing tables are touched. Everything is in userspace.

**Key Insight:** The "tunnel" is not a network concept — it's just a process reading from one fd and writing to another. The kernel sees nothing unusual.

### The exact 4-connection chain

```
curl
  ↓ TCP to 127.0.0.1:2746
kubectl (bind/listen on port 2746)
  ↓ WebSocket (SPDY) to kube-apiserver:443
kube-apiserver (on control plane EC2, e.g. 10.0.1.10)
  ↓ HTTPS to kubelet:10250 (on worker EC2, e.g. 10.0.5.23)
kubelet (on the same machine as the pod)
  ↓ TCP to pod IP:2746 (e.g. 10.244.3.17:2746)
argo-server pod
```

Port 2746 appears as a TCP port only at the two ends. In the middle it travels as data inside HTTP headers.

### 🔄 Refinement: Port-forward is not a single persistent connection for all requests

**My Misconception:** kubectl establishes one TCP connection to the pod and reuses it for all curl requests.

**The Correction:** kubectl keeps one persistent WebSocket to the API server. Each new curl creates a new **sub-stream** (stream ID) on that WebSocket. Each stream carries `port: 2746` in its header. The API server and kubelet open a new TCP connection to the pod per stream.

**Key Insight:** Multiplexing (SPDY/HTTP2) means many independent request lifecycles can share one underlying TCP connection. The persistent part is kubectl↔apiserver. The per-request part is kubelet↔pod.

### Where port 2746 is read as metadata (exactly 3 times)

1. **API server** reads `port: 2746` from the WebSocket stream header sent by kubectl
2. **Kubelet** reads `port: 2746` from the HTTP request sent by the API server
3. **Linux kernel on the worker node** reads port 2746 from the TCP packet header to route the connection into the correct pod network namespace

After these 3 reads, the chain is established and subsequent bytes flow blindly with no further port inspection.

### 🔄 Refinement: Two different IPs for one pod

**My Misconception:** The pod IP and the node IP are the same thing or closely related.

**The Correction:**
- `hostIP` (e.g. `10.0.5.23`) = the EC2 instance running the pod. The kubelet lives here.
- `podIP` (e.g. `10.244.3.17`) = the pod's own virtual IP, assigned to a virtual network interface inside the pod's Linux network namespace.

**Key Insight:** Multiple pods on the same machine each get their own unique IP via separate network namespaces and virtual ethernet pairs (veth). The CNI plugin allocates and wires these up. No two pods in the cluster share an IP.

### Why port-forward is needed at all (VPN context)

Your laptop can't reach `10.0.5.23` (worker node) or `10.244.3.17` (pod IP) directly — they're private IPs inside Razorpay's AWS VPC. VPN gives your laptop a virtual leg inside the VPC, making the kube-apiserver reachable. Port-forward then chains from the API server (reachable via VPN) through kubelet (VPC-internal) to the pod (same machine as kubelet).

### kubectl exec vs port-forward

Both use WebSocket to the API server as transport, but they do different things at the pod end:

| | port-forward | exec |
|---|---|---|
| What happens at pod | kubelet opens TCP to pod's port | kubelet spawns a new process inside container namespaces |
| What flows | raw TCP bytes | stdin/stdout/stderr of a process |
| Reusable | yes, multiple connections | no, one command per exec |

exec is not a wrapper over port-forward. Same transport layer, completely different operation.
