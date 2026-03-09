# Docker Build Task

**Task type:** `dphi.space.cg2.docker.build`

## Purpose
Build a Docker image from a Dockerfile in the user volume.

## Inputs
- `image.name` and `image.tag`: Output image name and tag.
- `volume`: Optional volume name to resolve the `dockerfile` and `context` paths. Defaults to the main users volume, *i.e.* `[username]-pvc`.
- `dockerfile`: Path to the Dockerfile (relative to the volume).
- `context`: Build context path (relative to the volume).

## Outputs
- `status`: Build status string.
- `message`: Optional error message.

## What it does
1. Renders a build sequence with the Dockerfile and context.
2. Runs the build sequence.
3. Returns the resulting image reference and status.

## Common failure reasons
- Image name or tag is missing.
- Dockerfile or context path is invalid.
- Build sequence fails.
