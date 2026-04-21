# Topic: VPN — Split Tunnel vs Full Tunnel

## What VPN actually does

A VPN makes your laptop appear to be inside a private network (e.g. Razorpay's AWS VPC) by:

1. Creating a **virtual network interface** (e.g. `utun3`) with an internal IP (e.g. `10.8.0.42`)
2. Installing **kernel routing rules** that redirect certain destination IPs to `utun3`
3. The VPN client process reads packets off `utun3`, **encrypts them**, and sends them over the internet to the VPN server
4. The VPN server decrypts and forwards packets into the private network — traffic appears to originate from `10.8.0.42`

## VPN is not a proxy

| | VPN | HTTP Proxy |
|---|---|---|
| Works at | Network layer (IP packets) | Application layer (HTTP) |
| App awareness | Apps are completely unaware | Apps must be configured to use it |
| How it intercepts | Kernel routing table redirects packets | App explicitly sends `CONNECT` to proxy |
| Scope | All TCP/UDP traffic for matched IPs | Only apps that speak HTTP proxy protocol |

## Split tunnel vs full tunnel

**Split tunnel** (most corporate VPNs):
- Only traffic to specific internal IP ranges goes through the VPN
- Routing rule: `10.0.0.0/8 → utun3` (only Razorpay's private range)
- YouTube, Google, etc. go directly out your wifi — VPN doesn't touch them
- Faster, less load on Razorpay's VPN server

**Full tunnel:**
- All traffic goes through the VPN
- Routing rule: `0.0.0.0/0 → utun3` (everything)
- Every packet — YouTube, personal email, everything — bounces through Razorpay
- Slower, Razorpay can see all your traffic, rarely used

## Why VPN + port-forward

Without VPN, your laptop (public internet) can't reach `10.0.1.10` (kube-apiserver inside AWS VPC).

With VPN, your laptop gets a virtual IP in the VPC range. The kube-apiserver becomes reachable. From there, port-forward chains through kubelet (VPC-internal) to the pod (same node as kubelet).

```
Without VPN:  laptop (49.207.x.x) ✗→ 10.0.1.10 (kube-apiserver)
With VPN:     laptop (10.8.0.42)  ✓→ 10.0.1.10 (kube-apiserver)
```

## Related questions

- [How does kubectl port-forward work end to end?](../questions/how_does_kubectl_port_forward_work_end_to_end.md)
