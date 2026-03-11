# Downlink task

**Task type:** `dphi.space.cg2.downlink`

## Purpose
Downlink files from a specific volume and file path onboard Clustergate-2 and store them in the namespace file area.

## Definition

```yaml
  - id: [task name]
    type: dphi.space.cg2.downlink
    description: [description]
    source:
      - logs.txt
      - example.yaml
    destination: /first_test
    volume: payload
```

## Inputs
- `id`: Name of the task.
- `description`: Description of the task.
- `source`: List of remote paths to downlink.
- `destination`: Namespace path where files should land after downlink is complete. Defaults to `/`.
- `volume`: Optional volume name to downlink the files from. Defaults to the main user's volume, *i.e.* `[username]-pvc`.

## Outputs
- `files`: List of files uploaded to the namespace paths.
- `uri`: Location of the downlink archive.
- `contentType`: Archive MIME type.
- `contentLength`: Archive size in bytes.


## Common failure reasons
- Source list is empty or contains invalid paths.
- Destination path is invalid.
