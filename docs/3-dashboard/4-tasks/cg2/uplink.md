# Uplink Task

**Task type:** `dphi.space.cg2.uplink`

## Purpose
Uplink files from namespace storage to a specific volume and filepath onboard Clustergate 2.

## Inputs
- `source`: List of filepaths to uplink from the namespace storage.
- `volume`: Optional volume name to uplink the files to. Defaults to the main users volume, *i.e.* `[username]-pvc`.
- `destination`: Folder onboard Clustergate-2 where to uplink all of the files, within the volume.

## Outputs
- `status`: Boolean success flag.
- `message`: Error message, if any.


## Common failure reasons
- One or more source files are missing on the ground storage.
- Remote destination is invalid.
