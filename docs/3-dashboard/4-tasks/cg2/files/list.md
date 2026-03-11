# Files list task

**Task type:** `dphi.space.cg2.files.list`

## Purpose
List files in a remote folder and return a structured file tree.

## Definition
```yaml
  - id: list_files
    type: dphi.space.cg2.files.list
    description: List files onboard
    folder: /
    volume: payload
    depth: 2
```

## Inputs
- `id`: Name of the task.
- `description`: Description of the task.
- `folder`: Target folder to list (defaults to `/`).
- `depth`: Max depth to include (defaults to 2).
- `volume`: Optional volume name to resolve the remote base path. Defaults to the main user's volume, *i.e.* `[username]-pvc`.

## Outputs
- `files`: Parsed file tree data.
- `uri`: Location of the downlinked archive.
- `contentType`: Archive MIME type.
- `contentLength`: Archive size in bytes.

## Common failure reasons
- Target folder is invalid.
- Downlink archive is missing or malformed.
