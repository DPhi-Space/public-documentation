# Specifications

For a more detailed EM API description, checkout the swagger file `em-api.json` and open it with [swagger editor](https://editor.swagger.io/).

## Storage Model

Each DPhi Pod name (`pod_name`) corresponds to a unique persistent private volume (PVC), on top of defining the name of the pod to be run. The rules are:

- Using an existing `pod_name` → reuses the same volume and its stored files.
- Using a new `pod_name` → creates a new, empty, dedicated volume.
- Omitting `pod_name` → uses the user's default pod and its default volume.
- All file operations (uplink, downlink, files_list, delete) and all pod runs use this same `pod_name`-to-volume mapping.
  - For example, running a pod with name pod `experiment-radiation` will use the `experiment-radiation` dedicated volume and mount it to the pod, under `/data`.

Files stored under one `pod_name` are NOT visible from another `pod_name`.

---

## **1. Uplink Files**

**Endpoint:** `POST /em/files/uplink`  
**Purpose:** Upload files from the client to the EM, storing them in the user's dedicated volume.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `files`: List of files to upload
  - `dest_path`: Relative path within the user's dedicated volume where files should be placed (optional)
  - `pod_name`: Specifies which persistent volume to upload to (optional)

**Response:**

- `200 OK` – Success:

```json
{
  "message": "Successfully uplinked files",
  "data": {
    "file_count": N,
    "total_size_kb": SIZE
  }
}
```

- `400 BAD REQUEST` – Errors such as:
  - Missing files

  ```json
  {
    "error": "NO_FILES",
    "message": "No files were provided for uplink!"
  }
  ```

  - Max uplink size exceeded

  ```json
  {
    "error": "MAX_UPLINK_SIZE_EXCEEDED",
    "message": "Total upload size exceeds 2 GB"
  }
  ```

- `423 LOCKED` – If CG2 is busy

**Notes:**

- The total size cannot exceed 2GB per API call.

---

## **2. List Files**

**Endpoint:** `GET /em/files/list`  
**Purpose:** Retrieve a list of files on the user's dedicated volume onboard the EM, including size and hash.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:**
  - `pod_name`: Specifies which persistent volume to list files from (optional)

**Response:**

- `200 OK` – Success:

```json
{
  "message": "Successfully listed files",
  "data": [
    {
      "type": "file",
      "name": "downlink.txt",
      "size": "167",
      "time": "2025-11-20-12-31",
      "hash": 5686952638663605203
    },
    {
      "type": "directory",
      "name": "echo-test",
      "size": "487",
      "time": "2025-11-20-11-30",
      "contents": [
        {
          "type": "file",
          "name": "Dockerfile",
          "size": "121",
          "time": "2025-11-20-13-43",
          "hash": -6285199279658827551
        },
        {
          "type": "file",
          "name": "echo-test.sh",
          "size": "362",
          "time": "2025-11-20-13-43",
          "hash": -8104029944333627578
        }
      ]
    }
  ]
}
```

- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Server side error.

---

## **3. Downlink File**

**Endpoint:** `GET /em/files/downlink`  
**Purpose:** Downlink a file from the user's dedicated volume on the EM. File is streamed as binary content with appropriate headers.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:**
  - `filepath`: Path of the file relative to the user's dedicated volume
  - `pod_name`: Specifies which persistent volume to downlink from (optional)

**Response:**

- `200 OK` – Success: File content streamed with `Content-Disposition` header containing filename
- `400 BAD REQUEST` – Error in path provided
- `403 FORBIDDEN` – Illegal path provided
- `404 NOT FOUND` – File missing
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Server side error

**Notes:**

- Returns file as a stream with metadata in headers including `Content-Disposition` with filename.

---

## **4. Delete File / Folder**

**Endpoint:** `POST /em/files/delete`  
**Purpose:** Remove a file or a folder from the user's dedicated volume.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `filepath`: Relative path to the file or folder
  - `pod_name`: Specifies which persistent volume to delete from (optional)

**Response:**

- `200 OK` – Success: `{ "message": "File deleted successfully" }`
- `400 BAD REQUEST` – File delete failed
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Internal execution error

---

## **5. Build Docker Image**

**Endpoint:** `POST /em/pod/image/build`  
**Purpose:** Build a Docker image using a provided Dockerfile and context.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `dockerfile`: Path to Dockerfile relative to volume
  - `context`: Build context path
  - `image`: Desired image name
  - `pod_name`: Specifies which persistent volume to use for build context (optional)

**Behavior:**

- Validates paths and constructs image name with user prefix.
- When the build fails, the last 100 lines of the Docker Build logs will be returned in the response. Previous Docker operations might be included in these logs.

**Response:**

- `200 OK` – Success: `{ "message": "Docker Image built successfully" }`
- `400 BAD REQUEST` – Build failed
  - Incorrect context path

    ```json
    {
      "error": "BUILD_FAILED",
      "message": "Docker build failed",
      "log_tail": [
        "unable to prepare context: path \"/clients/client1-pvc/new-software\" not found\n"
      ]
    }
    ```

  - Incorrect Dockerfile path provided

  ```json
  {
    "error": "BUILD_FAILED",
    "message": "Docker build failed",
    "log_tail": [
      "unable to prepare context: path \"/clients/client1-pvc/new-software\" not found\n",
      "#1 [internal] load build definition from Dockerfile.space\n",
      "#1 sha256:26a4faa40e92fc931d0c6a87f447a8032a3e79b17888b77db9b0ef13edfee70a\n",
      "#1 transferring dockerfile: 2B done\n",
      "#1 DONE 0.1s\n",
      "\n",
      "#2 [internal] load .dockerignore\n",
      "#2 sha256:acb2bf344520a6e236ecc0eb1a950b4c6d16040e302d249f7af69f8bdcba3882\n",
      "#2 transferring context: 2B done\n",
      "#2 DONE 0.2s\n",
      "failed to solve with frontend dockerfile.v0: failed to read dockerfile: open /varlibdocker/daemon-data/tmp/buildkit-mount2195845686/Dockerfile.space: no such file or directory\n"
    ]
  }
  ```

- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Server side error

---

## **6. Load Docker Image**

**Endpoint:** `POST /em/pod/image/load`  
**Purpose:** Load a Docker image from a tar file. The `image` name provided in the request must match the one used during the Docker build. The tar file must already be present onboard.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `tarfile`: Path to tar file relative to volume
  - `image`: Image name (must match the name used during Docker build)
  - `pod_name`: Specifies which persistent volume contains the tarfile (optional)

**Response:**

- `200 OK` – Success: `{ "message": "Tar file loaded successfully" }`
- `400 BAD REQUEST` – Invalid path or load failure

```json
{
  "error": "IMAGE_LOAD_FAILED",
  "message": "Docker Image tarfile failed to load",
  "log_tail": [
    "sh: line 1: /clients/client1-pvc/test2.tar: No such file or directory\n"
  ]
}
```

- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Execution errors

---

## **7. List Docker Images**

**Endpoint:** `GET /em/pod/image/list`  
**Purpose:** Retrieve a list of Docker images available for the user. Returns a JSON array of all the Docker images built and loaded by the user. Publicly available Docker images are not listed here.

**Request:**

- **Headers:** `Authorization: Bearer <token>`

**Response:**

- `200 OK` – Success: `{ "message": "Successfully loaded list of docker images", "data": [ ... ] }`
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Internal Server Error

---

## **8. Create Namespace**

**Endpoint:** `POST /em/pod/namespace/create`  
**Purpose:** Request a namespace creation for user owned inter-pod communication. Creates a namespace with the username as a prefix, enabling DPhi Pods of the given user to communicate with each other onboard. Pods must be requested to run inside the namespace by setting the namespace flag on the request.

**Request:**

- **Headers:** `Authorization: Bearer <token>`

**Response:**

- `200 OK` – Success: `{ "message": "Namespace created successfully" }`
- `400 BAD REQUEST` – Namespace creation failed
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Internal server error

**Notes:**

- Required before pods can expose ports and communicate with each other
- All pods running with `namespace=true` will be placed in this private namespace

---

## **9. Execute DPhi Pod**

**Endpoint:** `POST /em/pod/run`  
**Purpose:** Run a container/pod with a specified Docker image.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `image` :
    - Type: `string`
    - Required: True
    - Description: Docker image name
    - Example: `python:3.11-alpine`
  - `max_duration`:
    - Type: `int`
    - Required: True
    - Description: Maximum execution time in minutes
    - Example: `30`
  - `node`:
    - Type: `string`
    - Required: True
    - Description: Target node on which to run the DPhi Pod - FPGA, GPU, or MPU.
    - Example: `FPGA`
  - `scheduled_time`
    - Type: `string`
    - Required: False
    - Description: ISO format timestamp with timezone.
    - Example: `2025-05-22T12:10:00+02:00`
  - `command` <string>
    - Type: `string`
    - Required: False
    - Description: Override default Docker image command.
    - Example: `echo 'is it this simple to run in space?' > hello-space.txt`
  - `pod_name`:
    - Type: `string`
    - Required: False
    - Description: Specifies which persistent volume to mount at /data.
    - Example: `experiment-radiation`
  - `ports`:
    - Type: `list[int]`
    - Required: False
    - Description: List of ports to expose. It requires the namespace to be created beforehand.
    - Example: `[80, 1999, 14]`
  - `namespace`:
    - Type: `bool`
    - Required: False
    - Description: Run pod in private namespace.
    - Example: `[80, 1999, 14]`

**Response:**

- `200 OK` – Success: `{ "message": "Docker run scheduled successfully" }`
- `400 BAD REQUEST` – Invalid parameters
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Execution failure

**Notes:**

- The DPhi Pod will be gracefully stopped by the system after the execution time goes over max_duration in minutes.
- `scheduled_time` must be provided in ISO format with timezone, e.g. `2025-05-22T12:10:00+02:00`
- Providing the `command` parameter will override the Docker image's default command. If none is provided, the default command embedded in the Docker image will be executed.
- Each `pod_name` maps to a dedicated persistent volume:
  - Using an existing `pod_name` mounts its existing volume (files preserved)
  - Using a new `pod_name` creates a new, empty volume
  - Omitting `pod_name` uses the user's default pod and its default volume
- Port exposure requires:
  - A namespace must be created first using the namespace creation endpoint
  - The `namespace` parameter must be set to `true`
  - Pods in the same namespace can communicate via `<username>-<`pod_name`>:<port>`

---

## **10. Check DPhi Pod Status**

**Endpoint:** `GET /em/pod/status`  
**Purpose:** Get the current DPhi Pod status. When a DPhi Pod is scheduled, it will always succeed, even though the deployment might be blocked (e.g. incorrect image name, node selected not yet available). Therefore, always check the DPhi Pods status after scheduling it.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:**
  - `pod_name`: Identifies which pod instance to query (optional)

**Response:**

- `200 OK` – Successfully fetched DPhi Pod status.
  - DPhi Pod successfully scheduled:

  ```json
  {
    "message": "Successfully fetched DPhi Pod status",
    "data": {
      "state": {
        "running": {
          "startedAt": "2025-11-20T12:31:12Z"
        }
      }
    }
  }
  ```

  - DPhi Pod failed to be scheduled:

    ```json
    {
      "message": "Successfully fetched DPhi Pod status",
      "data": {
        "state": {
          "waiting": {
            "message": "Back-off pulling image \"client1-echo-test12\": ErrImagePull: rpc error: code = NotFound desc = failed to pull and unpack image \"docker.io/library/client1-echo-test12:latest\": failed to resolve reference \"docker.io/library/client1-echo-test12:latest\": docker.io/library/client1-echo-test12:latest: not found",
            "reason": "ImagePullBackOff"
          }
        }
      }
    }
    ```

- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Execution failure

---

## **Shared Behaviors**

- All endpoints require **authenticated users**.
- Error code `423 LOCKED` prevents concurrent requests.
- All file operations and pod executions respect the `pod_name`-to-volume mapping described in the Storage Model section.

---

Checkout an [Example](/docs/4-em-api/03-example.md) implementation.
