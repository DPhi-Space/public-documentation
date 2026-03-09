# DPhi Pod Run Task

**Task type:** `dphi.space.cg2.pod.run`

## Purpose
Launch a pod run on Clustergate 2 using a container image and runtime settings.

## Inputs
- `image.name` and `image.tag`: Container image reference.
- `command` and `args`: Optional command override.
- `env`: Environment variables list.
- `ports`: Container port mappings.
- `node`: Target node (FPGA, MPU, or GPU).
- `max_duration_seconds`: Optional run timeout.
- `volume`: Optional volume name to mount to the DPhi Pod. Defaults to the main users volume, *i.e.* `[username]-pvc`.

## Outputs
- `status`: Boolean success flag.
- `message`: Optional error message.

## Common failure reasons
- Image name or tag is missing.
- Node selection is invalid.
- Remote manifest upload fails.
- Sequence execution fails.
