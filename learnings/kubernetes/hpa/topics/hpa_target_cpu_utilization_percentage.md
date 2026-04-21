# Topic: HPA targetCPUUtilizationPercentage

## Definition

`targetCPUUtilizationPercentage` is the HPA metric that controls when Kubernetes scales pods in or out. It is a percentage of the pod's **CPU request** (not limit, not node CPU).

## How it works

```
target_cpu_per_pod = targetCPUUtilizationPercentage% × requests.cpu

desired_replicas = ceil(total_actual_cpu / target_cpu_per_pod)
```

**Example:**
- `requests.cpu: 200m`, `targetCPUUtilizationPercentage: 40`
- Target per pod = `80m`
- If 10 pods are consuming `1200m` total → HPA scales to `ceil(1200/80) = 15`

## Tradeoffs

| Lower % (e.g. 40) | Higher % (e.g. 50–60) |
|---|---|
| Scales out earlier, more headroom | More efficient pod utilization |
| Risk of unnecessary scale-out / flapping | Risk of getting caught by sudden bursts |
| Better for unpredictable traffic spikes | Better for steady, predictable load |

## Scale-down stabilization

Kubernetes applies a default **5-minute stabilization window** for scale-down to prevent flapping. Scale-out has no stabilization window by default (immediate).

## Relationship with `requests.cpu`

Setting `requests.cpu` too low (e.g. `100m` when actual usage is `300m`) makes HPA think pods are 3x more loaded than the target, causing aggressive over-scaling. Always set requests to a realistic baseline.

## Related questions

- [HPA CPU target percentage meaning and tradeoffs](../questions/hpa_cpu_target_percentage_meaning_and_tradeoffs.md)
