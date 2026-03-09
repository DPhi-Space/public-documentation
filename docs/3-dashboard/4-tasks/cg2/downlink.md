# Downlink Task

**Task type:** `dphi.space.cg2.downlink`

## Purpose
Downlink files from a specific volume and filepath onboard Clustergate 2 and store them in the namespace file area.

## Inputs
- `source`: List of remote paths to downlink.
- `volume`: Optional volume name to downlink the files from. Defaults to the main users volume, *i.e.* `[username]-pvc`.
- `destination`: Namespace path where files should land after downlink is complete. Defaults to `/`.

## Outputs
- `files`: List of files uploaded to the namespace paths.
- `uri`: Location of the downlink archive.
- `contentType`: Archive MIME type.
- `contentLength`: Archive size in bytes.


## Common failure reasons
- Source list is empty or contains invalid paths.
- Destination path is invalid.
