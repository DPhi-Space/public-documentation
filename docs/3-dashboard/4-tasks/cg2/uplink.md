# Uplink Task

**Task type:** `dphi.space.cg2.uplink`

## Purpose
Uplink files from namespace storage to a specific volume and file path onboard Clustergate-2.

## Definition

```yaml
  - id: [task name]
    type: dphi.space.cg2.uplink
    description: [task description]
    source:
      - config.yaml
      - /tests/calibration.json
    destination: /data/config
    volume: payload
```

## Inputs
- `id`: Name of the task.
- `description`: Description of the task.
- `source`: List of file paths to uplink from the namespace storage.
- `destination`: Folder onboard Clustergate-2 where to uplink all of the files, within the volume.
- `volume`: Optional volume name to uplink the files to. Defaults to the main user's volume, *i.e.* `[username]-pvc`.

## Outputs
- `status`: Boolean success flag.
- `message`: Error message, if any.


## Common failure reasons
- One or more source files are missing on the ground storage.
- Remote destination is invalid.
