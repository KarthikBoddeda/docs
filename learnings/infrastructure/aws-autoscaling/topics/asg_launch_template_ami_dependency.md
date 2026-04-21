# Topic: ASG Launch Template AMI Dependency Chain

## Definition

AWS Auto Scaling Groups (ASGs) use **Launch Templates** to define instance configurations. Launch Templates reference **AMIs** (Amazon Machine Images), which are backed by **EBS Snapshots**. This creates a multi-layer dependency chain where deleting any lower layer breaks everything above it.

## The Dependency Chain

```
Auto Scaling Group (ASG)
    │
    │  references
    ▼
Launch Template (version N)
    │
    │  specifies
    ▼
AMI (ami-0abc123...)
    │
    │  backed by
    ▼
EBS Snapshot(s) (snap-0def456...)
    │
    │  contains
    ▼
Actual disk data (root volume, data volumes)
```

## What Happens When You Delete a Snapshot

| Action | Immediate Effect | Delayed Effect |
|---|---|---|
| Delete snapshot | AMI becomes "invalid" | Next ASG scale-out **fails** |
| Deregister AMI | Launch Template references stale AMI | Next ASG scale-out **fails** |
| Delete Launch Template | ASG has no template | ASG **cannot scale at all** |

**Critical:** Deleting a snapshot doesn't immediately cause any error. The failure only manifests when the ASG **next tries to launch an instance** — which could be hours or days later.

## The Delayed-Fuse Pattern

```
Time 0:  Snapshot deleted (no error, no alert)
Time 0-N: Cluster has enough capacity, no scaling needed
Time N:  Traffic spike → ASG tries to scale out
         → Launch Template → AMI → Snapshot not found!
         → Instance launch fails
         → No new nodes join Kubernetes cluster
         → Pods stuck in Pending
         → Outage
```

The gap between "cause" (snapshot deletion) and "symptom" (pods stuck) makes root-causing extremely difficult. The person investigating sees "pods won't schedule" and has no reason to think about snapshot lifecycle.

## How Cleanup Automations Get This Wrong

Typical snapshot cleanup logic:

```python
# INCOMPLETE — only checks direct AMI references
for snapshot in list_snapshots(older_than="30d"):
    amis_using = find_amis_using_snapshot(snapshot.id)
    if len(amis_using) == 0:
        delete_snapshot(snapshot.id)  # DANGEROUS
```

This misses:
1. **Launch Templates** still referencing the AMI
2. **ASGs** still referencing those Launch Templates
3. **Terraform state** that expects the snapshot to exist
4. **Backup/rollback scenarios** where you might need to recreate the AMI

### Safe cleanup logic

```python
for snapshot in list_snapshots(older_than="30d"):
    amis = find_amis_using_snapshot(snapshot.id)
    if len(amis) > 0:
        continue  # still referenced by AMI

    # Check deeper: are any AMIs referenced by launch templates?
    for ami in find_all_amis_from_snapshot_lineage(snapshot.id):
        launch_templates = find_launch_templates_using_ami(ami.id)
        if len(launch_templates) > 0:
            continue  # still in use

    # Safe to delete (with dry-run first!)
    if DRY_RUN:
        log(f"Would delete: {snapshot.id}")
    else:
        delete_snapshot(snapshot.id)
```

## Best Practices

1. **Always check the full dependency tree** before deleting infrastructure resources
2. **Add dry-run modes** to all destructive automations
3. **Tag resources in use** — e.g., `in-use-by: asg/my-cluster` on snapshots
4. **Alert on launch failures** — don't wait for pod-level symptoms
5. **Decouple cleanup from hard-delete** — mark for deletion, wait N days, then delete

## Related

- [Destructive automation safeguards](./destructive_automation_safeguards.md)
- [Story: Phantom Snapshot Devstack Outage](/learnings/stories/phantom-snapshot-devstack-outage.md)
