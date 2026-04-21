# Topic: Destructive Automation Safeguards

## Definition

**Destructive automations** are automated processes that delete, modify, or decommission infrastructure resources. They need specific safeguards because their blast radius is typically environment-wide and their failures are often delayed (the damage isn't visible until the resource is next needed).

## Why Automation Failures Are Worse Than Manual Failures

| Property | Manual operation | Automated operation |
|---|---|---|
| **Awareness** | Human knows they did it | No human is aware |
| **Scope** | Usually one resource | Can affect many resources in a loop |
| **Timing** | Happens when someone is watching | Can happen at 3 AM |
| **Audit trail** | Person remembers | Only if explicitly logged |
| **Rollback** | Person can undo immediately | May be irreversible before anyone notices |

## The Safeguard Checklist

### 1. Dry-run mode (always default)

```python
DRY_RUN = True  # Default to safe mode

if DRY_RUN:
    log(f"[DRY RUN] Would delete: {resource.id}")
else:
    delete(resource.id)
```

Every destructive automation should have a dry-run mode that is the **default**. The operator must explicitly opt into destructive mode.

### 2. Dependency tree validation

Before deleting resource X, verify nothing depends on X:

```
Resource X
├── Direct references (e.g., AMIs using this snapshot)
├── Indirect references (e.g., Launch Templates → AMIs → snapshot)
├── Terraform state references
└── Cross-account references
```

### 3. Deletion delay (soft-delete → hard-delete)

```
Day 0: Mark resource as "pending deletion" (tag it, don't delete)
Day 7: If no one objected → actually delete
```

This gives humans a window to notice and intervene.

### 4. Blast radius limits

```python
MAX_DELETIONS_PER_RUN = 10

deleted = 0
for resource in candidates:
    if deleted >= MAX_DELETIONS_PER_RUN:
        log("Hit deletion limit, stopping. Review remaining candidates.")
        break
    delete(resource)
    deleted += 1
```

Prevent runaway automation from deleting everything.

### 5. Alert on deletion

Send a Slack/PagerDuty notification for every deletion, not just failures:

```
[Cleanup Bot] Deleted 3 snapshots: snap-abc, snap-def, snap-ghi
              Skipped 12 (still in use)
              Next run: 2026-03-10
```

### 6. Resource tagging

Tag resources with their purpose and owner:

```
Tags:
  managed-by: cleanup-automation
  in-use-by: asg/prod-api-cluster
  do-not-delete: true  (manual override)
  created-by: terraform/module/api
```

The automation should respect `do-not-delete` and `in-use-by` tags.

### 7. Post-deletion health check

After deleting resources, verify the dependent systems still work:

```python
delete_snapshots(candidates)

# Verify ASGs can still launch
for asg in affected_asgs:
    test_launch = asg.dry_run_launch()
    if not test_launch.success:
        alert(f"ASG {asg.name} cannot launch after cleanup!")
        rollback()
```

## Common Automation Targets and Their Risks

| Resource | Cleanup risk | Mitigation |
|---|---|---|
| **EBS Snapshots** | Breaks AMIs → ASG scaling | Full dependency tree check |
| **AMIs** | Breaks Launch Templates | Check all LT versions, not just latest |
| **ECR Images** | Breaks deployments | Keep N recent images, tag releases |
| **S3 Objects** | Data loss | Versioning + lifecycle policies |
| **DNS Records** | Service discovery breaks | Never auto-delete DNS |
| **IAM Roles** | Permission failures | Check for active sessions/attachments |

## Related

- [ASG launch template AMI dependency](./asg_launch_template_ami_dependency.md)
- [Story: Phantom Snapshot Devstack Outage](/learnings/stories/phantom-snapshot-devstack-outage.md)
