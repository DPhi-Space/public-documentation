# Python Client Example

This Python script demonstrates how to interact with the **EM API** for file management, Docker image operations, and DPhi Pods execution. It covers authentication, file uplink/downlink, Docker image build/load/list, running DPhi Pods, and cleanup.

---

## **1. Authentication**

The client first obtains a JWT access token to authorize requests.

```python
def get_token():
    response = requests.post(
        BASE_URL + "auth/",
        data={"username": username, "password": password},
    )
    content = response.json()
    TOKEN = content["access"]
```

All subsequent requests use this token via helper functions:

```python
def ensure_token():
    """
    Ensures TOKEN exists. If not, fetch a new one.
    """
    if TOKEN is None:
        print("No token found. Fetching new token...")
        if not get_token():
            raise Exception("Authentication failed.")

def authorized_get(url, **kwargs):
    """
    Wrapper for GET requests with Authorization header and auto-refresh logic.
    """
    ensure_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TOKEN}"

    response = requests.get(url, headers=headers, **kwargs)

    # Retry if token expired
    if response.status_code == 401:
        print("Token expired. Refreshing...")
        if get_token():
            headers["Authorization"] = f"Bearer {TOKEN}"
            response = requests.get(url, headers=headers, **kwargs)

    return response


def authorized_post(url, **kwargs):
    """
    Wrapper for POST requests with Authorization header and auto-refresh logic.
    """
    ensure_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TOKEN}"

    response = requests.post(url, headers=headers, **kwargs)

    # Retry if token expired
    if response.status_code == 401:
        print("Token expired. Refreshing...")
        if get_token():
            headers["Authorization"] = f"Bearer {TOKEN}"
            response = requests.post(url, headers=headers, **kwargs)

    return response
```

---

## **2. File Operations**

### **Uplink Files**

Upload multiple files to a specific folder on the user's private volume on the EM:

```python
def uplink(filepaths, dest_path=""):
    """
    Upload multiple files to the users dedicated volume on CG2.

    filepaths: list of local paths to upload
    dest_path: remote destination folder
    """
    ensure_token()
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Prepare files for multipart upload
    files_to_upload = []
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        files_to_upload.append(("files", (filename, open(filepath, "rb"))))

    response = requests.post(
        BASE_URL + "em/files/uplink",
        headers=headers,
        files=files_to_upload,
        data={"dest_path": dest_path},
    )

    # Clean up file handles
    for _, (_, file_obj) in files_to_upload:
        file_obj.close()

    return response.json()

```

- `filepaths`: list of local files to upload
- `dest_path`: remote folder path

### **List Files**

Retrieve a JSON list of files present in the user's private volume on the EM, with metadata:

```python
def files_list():
    """
    Retrieve a list of files on the users dedicated volume on CG2.
    """
    response = authorized_get(BASE_URL + "/em/files/list")
    return response.json()
```

### **Downlink Files**

Downlink a file from the user's private volume on the EM:

```python
def downlink(filepath, downlink_folder="downlink/"):
    """
    Downlink a file from the users dedicated volume and save it locally.

    Backend returns base64 content + metadata.
    """
    response = authorized_get(
        BASE_URL + "/em/files/downlink",
        params={"filepath": filepath},
    )

    if response.status_code != 200:
        return response.json()

    data = response.json()

    # Decode BASE64 content
    filename = data["filename"]
    file_bytes = base64.b64decode(data["content"])

    # Prepare local folder
    os.makedirs(downlink_folder, exist_ok=True)
    local_path = os.path.join(downlink_folder, filename)

    # Write file
    with open(local_path, "wb") as f:
        f.write(file_bytes)

    print(f"File '{filename}' saved to {local_path}")
    return data
```

This saves the file locally in a `downlink/` folder.

### **Delete Files**

Delete files or directories on the user's private volume on the EM:

```python
def delete(filepath):
    """
    Delete a file on the users dedicated folder on CG2.
    """
    response = authorized_post(
        BASE_URL + "em/files/delete",
        data={"filepath": filepath},
    )
    return response.json()

```

---

## **3. Docker Image Operations**

### **Build Docker Image**

Build a Docker image remotely using a Dockerfile and context directory:

```python
def image_build(dockerfile, image, context="."):
    """
    Build a Docker image on CG2. The image is built on an air-gapped environment.
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/build",
        data={"dockerfile": dockerfile, "image": image, "context": context},
    )
    return response.json()
```

- `dockerfile`: path to Dockerfile on the user's private volume on the EM
- `image_name`: name of the Docker image
- `context`: folder context for the build on the user's private volume on the EM

### **Load Docker Image**

Load a prebuilt tar image that has already been uplinked to the user's private volume on the EM:

```python
def image_load(tarfile, image):
    """
    Load a Docker image tarball on CG2.
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/load",
        data={"tarfile": tarfile, "image": image},
    )
    return response.json()
```

### **List Docker Images**

List available Docker images for the user.

```python
def image_list():
    """
    List available Docker images on the EM for the user.
    """
    response = authorized_get(BASE_URL + "em/pod/image/list")
    return response.json()
```

---

### Run Docker Image (Pod Execution)\*\*

Run a DPhi Pod on the EM from an already built Docker Image. Doing so will stop any previous instance of a DPhi Pod ran by the same user.

```python
def run(image, node="FPGA", max_duration=1, command="", scheduled_time=None):
    """
    Run a DPhi Pod on the EM with maximum execution time in minutes.

    image: Docker image to run
    node: node on which to run the DPhi Pod [FPGA,GPU,MPU]
    max_duration: maximum execution duration of the DPhi Pod in minutes before the system stops it gracefully.
            "max_duration": max_duration,
            "command": command,
            "scheduled_time": scheduled_time,
        },
    )
    return response.json()
```

- `image`: Docker image to run inside the DPhi Pod
- `max_duration`: runtime limit in minutes before gracefully stopping the container.
- `node`: Node on which to run the DPhi Pod [FPGA,GPU,MPU],
- `command`(optional): Linux bash command to run when starting the DPhi Pod. If none is provided, the default command embedded in the Docker image.
- `scheduled_time`(optional): time when to schedule the DPhi Pods execution. If none is provided, it will be scheduled as soon as possible. Time format should be provided in ISO format, e.g. `2025-05-22T12:10:00+02:00`.

---

### DPhi Pod Status

Get the current DPhi Pod execution status.

```python
def pod_status():
    """
    Get current DPhi Pod execution status.
    """
    response = authorized_get(BASE_URL + "em/pod/status")
    return response.json()
```

---

## **5. Example Workflow**

A typical workflow in the script:

```python
# Authenticate
get_token()

# List current files
files_list()

# Upload files
uplink(["Dockerfile", "echo-test.sh"], dest_path="echo-test")

# Build Docker image
image_build("./echo-test/Dockerfile", "echo-test", "./echo-test")

# Downlink a file
downlink("/echo-test/Dockerfile")

# Run Docker container
run("echo-test")

# Cleanup files
delete("/echo-test/Dockerfile")
delete("downlink.txt")
```

This demonstrates a complete EM API flow:

1. Authenticate
2. Upload files
3. Build Docker Image
4. Run Docker Image/Pod execution
5. Downlink Files
6. Cleanup

---

## **6. Notes**

- All file content for downlink is returned in **Base64** encoding.
- The client automatically refreshes the JWT token if expired.
- The BASE_URL will be provided to the user once the EM is reserved.
- Docker Images built on board will have the user's name prefixed to it for filtering, and only these Docker Images can be executed by the user. This will be automatically managed by the backend when requesting builds. However, when loading tar files, the user is responsible for tagging the Docker Image with it's username. Otherwise, it will be impossible to run the execute the given Docker Image.

---

Checkout the [FAQ](/docs/clients/em-api/04-faq.md).
