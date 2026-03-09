# Docker Image List Task

**Task type:** `dphi.space.cg2.docker.image.list`

## Purpose
Return a list of available container images from the Clustergate 2 registry.

## Inputs
- No user inputs; it uses the current execution context.

## Outputs
- `images`: List of images with repository, tag, id, created time, and size.
- `uri`: Location of the downlinked output file.
- `contentLength`: Output size in bytes.

## Common failure reasons
- Downlink output is missing.
- Sequence execution fails.
