# Topic: kubectl port-forward

## What it is

`kubectl port-forward` makes a pod's port reachable on your local machine by stitching together 4 TCP connections across 3 relay processes. No routing tables are modified. Everything runs in userspace.

## The 4-connection chain

```
curl
  ↓  TCP  →  127.0.0.1:2746     (kubectl listens here via bind/listen)
kubectl
  ↓  WebSocket (SPDY)  →  kube-apiserver:443
kube-apiserver
  ↓  HTTPS  →  kubelet:10250    (on the worker node)
kubelet
  ↓  TCP  →  podIP:2746         (direct connection inside the node)
pod
```

## What "stitching" means

Each relay process does exactly this:

```c
while (true) {
    bytes = read(left_fd);
    write(right_fd, bytes);
    bytes = read(right_fd);
    write(left_fd, bytes);
}
```

No content inspection. No protocol parsing. Blind byte copying between two file descriptors.

## Port metadata flow

Port 2746 is passed as **data in HTTP headers**, not as TCP ports, for the middle two connections:

| Connection | TCP port used | How 2746 travels |
|---|---|---|
| curl → kubectl | 2746 (real TCP port) | — |
| kubectl → API server | 443 | `port: 2746` in WebSocket stream header |
| API server → kubelet | 10250 | `port: 2746` in HTTP request |
| kubelet → pod | 2746 (real TCP port) | — |

## Multiple curl requests

kubectl maintains one persistent WebSocket to the API server. Each new `curl` creates a new sub-stream (with its own stream ID and `port: 2746` header) on that WebSocket. Each stream gets its own TCP connection from kubelet to the pod.

## The WebSocket upgrade

kubectl starts with a normal HTTP request:
```
GET /api/v1/namespaces/argo/pods/argo-server-xyz/portforward
Upgrade: websocket
```
After the server responds `101 Switching Protocols`, both sides stop speaking HTTP. The connection becomes a bidirectional frame-based stream — either side can send at any time.

## Related questions

- [How does kubectl port-forward work end to end?](../questions/how_does_kubectl_port_forward_work_end_to_end.md)
