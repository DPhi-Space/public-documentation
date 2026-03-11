# Docker image list task

**Task type:** `dphi.space.cg2.docker.image.list`

## Purpose
Return a list of available container images from the Clustergate-2 registry.

## Definition
```yaml
  - id: [task name]
    type: dphi.space.cg2.docker.image.list
    description: [task description]
```

## Inputs
- `id`: Name of the task.
- `description`: Description of the task.

## Outputs
- `images`: List of images with repository, tag, id, created time, and size.
- `uri`: Location of the downlinked output file.
- `contentLength`: Output size in bytes.

## Common failure reasons
- Downlink output is missing.
- Sequence execution fails.
