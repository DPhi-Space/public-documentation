# Specifications

For a more detailed EM API description, checkout the swagger file `em-api.json` and open it with [swagger editor](https://editor.swagger.io/).

## **1. Uplink Files**

**Endpoint:** `POST /em/files/uplink`
**Purpose:** Upload files from the client to the EM, storing them in the user’s dedicated volume.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Form Data:**
  - `files`: List of files to upload
  - `dest_path`: Relative path within the user’s dedicated volume where files should be placed

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
    "message": f"Total upload size exceeds 500 MB",
  }
  ```

- `423 LOCKED` – If CG2 is busy

**Notes:**

- The total size cannot exceed 500 MB per API call.

---

## **2. List Files**

**Endpoint:** `GET /em/files/list`
**Purpose:** Retrieve a list of files on the user’s dedicated volume onboard the EM, including size and hash.

**Request:**

- **Headers:** `Authorization: Bearer <token>`

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
**Purpose:** Downlink a file from the user’s dedicated volume on the EM. File data is returned in base64 encoding in the response.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:**
  - `filepath` – Path of the file relative to the user’s dedicated volume

**Behavior:**

**Response:**

- `200 OK` – Success:

```json
{
  "content": "<base64-encoded>",
  "filename": "example.txt",
  "size": 12345,
  "hash": "<sha256-hash>"
}
```

- `400 BAD REQUEST` – Error in path provided
- `403 FORBIDDEN` - Illegal path provided
- `404 NOT FOUND` – File missing
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Server side error

  **Notes:**

- Encodes content in base64, returns metadata including size and SHA256 hash.

---

## **4. Delete File / Folder**

**Endpoint:** `POST /em/files/delete`
**Purpose:** Remove a file or a folder from the user’s dedicated volume.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **JSON Body:** `{ "filepath": "<relative_path>" }`

**Behavior:**

- Remove the target file path.

**Response:**

- `200 OK` – Success: `{ "message": "File deleted successfully" }`
- `400 BAD REQUEST` – File delete failed
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Internal execution error

---

## **5. Build Docker Image**

**Endpoint:** `POST /em/pod/image/build`
**Purpose:** Build a Docker image using a provided Dockerfile and context. The user's name will be prepended to the Docker Image provided.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **JSON Body:**

```json
{
  "dockerfile": "<path_relative_to_volume>",
  "context": "<context_path>",
  "image_name": "<desired_image_name>"
}
```

**Behavior:**

- Validates paths and constructs image name with user prefix.
- When the build fails, the last 100 lines of the Docker Build logs will be returned in the response.

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

**Endpoint:** `POST /em/image/load`
**Purpose:** Load a Docker image from a tar file. The `image` name provided in the request must match the one used during the docker build.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **JSON Body:** `{ "tarfile": "<path_relative_to_volume>", "image":<image_name> }`

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

**Endpoint:** `GET /em/image/list`
**Purpose:** Retrieve a list of Docker images available for the user. Returns a JSON array of all the docker images built and loaded by the user.

**Request:**

- **Headers:** `Authorization: Bearer <token>`

**Response:**

- `200 OK` – Success: `{ "message": "Successfully loaded list of docker images", "data": [ ... ] }`
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – JSON parsing or SCP failures

---

## **8. Execute DPhi Pod**

**Endpoint:** `POST /em/pod/execution`
**Purpose:** Run a container/pod with a specified Docker image.

**Request:**

- **Headers:** `Authorization: Bearer <token>`
- **JSON Body:**

```json
{
  "docker_image": "<image_name>", // required
  "max_duration": 30, // required
  "node": "FPGA", // required
  "scheduled_time": "<time in isoformat>", // optional
  "command": "<command>" // optional
}
```

**Response:**

- `200 OK` – Success: `{ "message": "Docker run scheduled successfully" }`
- `423 LOCKED` – If CG2 is busy
- `500 INTERNAL ERROR` – Execution failure

Notes:

- The DPhi Pod will be gracefully stopped by the system after the execution time goes over max_duration in minutes.
- `scheduled_time` must be provided in ISO format with timezone, e.g. `2025-05-22T12:10:00+02:00`
- Providing the `command` parameter will override the Docker image's default command. If none is provided, the default command embedded in the Docker image will be executed.

---

## **9. Check DPhi Pod Status**

**Endpoint:** `GET /em/pod/status`
**Purpose:** Get the current DPhi Pod status. When a DPhi Pod is scheduled, it will always succeed, even though the deployment might be blocked (e.g. incorrect image name, node selected not yet available). Therefore, always check the DPhi Pods status after scheduling it.

**Request:**

- **Headers:** `Authorization: Bearer <token>`

**Behavior:**

- Retrieves the current DPhi Pod status

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

### **Shared Behaviors**

- All endpoints require **authenticated users**.
- Concurrent requests will return error `423 LOCKED` prevents concurrent requests.

---

Checkout an [Example](/docs/4-em-api/03-example.md) implementation.
