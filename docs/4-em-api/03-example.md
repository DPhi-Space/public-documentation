# Python Client Example

The `em-api-interface.py` script exemplifies how to create a client wrapper for the EM API specifications. It can be found under the [`examples/em-api/`](https://github.com/DPhi-Space/public-documentation/tree/main/examples/em-api) folder, with all the necessary support files for running the examples.

## Overview

This Python client provides a simple interface for interacting with the CG2 EM API. It handles authentication, file operations, Docker image management, and DPhi Pod execution through a set of helper functions that abstract the underlying REST API calls.

## Key Features

- **Automatic authentication** with token management and refresh
- **File operations**: uplink, downlink, list, and delete files
- **Docker image management**: build from Dockerfile, load from tarball, and list available images
- **Pod execution**: run containers on FPGA, GPU, or MPU nodes with scheduling support
- **Namespace management**: create namespaces for inter-pod communication
- **Storage model support**: full integration with pod-name-to-volume mapping

## Getting Started

### Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Access credentials (username and password)

### Basic Setup

```python
import requests
from em_api_interface import *

# Authentication happens automatically on first API call
# Or explicitly with:
get_token()
```

## Understanding the Storage Model

Before diving into examples, it's important to understand how storage works:

- Each `pod_name` corresponds to a unique persistent volume
- Using an existing `pod_name` → reuses the same volume and files
- Using a new `pod_name` → creates a new, empty volume
- Omitting `pod_name` → uses your default volume
- Files in one pod's volume are NOT visible to other pods

This applies to all operations: file uplink/downlink, Docker builds, and pod runs.

## Examples

The script includes three comprehensive examples demonstrating different aspects of the API:

### 1. Simple Operations (`example_simple_operations`)

This example demonstrates the basic workflow for working with files and running pods:

**What it does:**

- Lists files in the default volume
- Uplinks a Dockerfile and shell script to a specific directory
- Builds a Docker image from the uploaded files
- Runs the image on the default FPGA node
- Runs the same image on GPU with a custom command
- Schedules a pod to run at a specific future time
- Downlinks generated output files
- Cleans up by deleting uploaded and generated files

**Key concepts:**

- Basic file operations (uplink, list, downlink, delete)
- Docker image building from volume files
- Pod execution with and without custom commands
- Scheduled pod execution with timezone support
- Pod status checking

**Code snippet:**

```python
# Upload files to a directory
uplink(["./Dockerfile", "./echo-test.sh"], dest_path="echo-test")

# Build image from uploaded files
image_build("./echo-test/Dockerfile", "echo-test", "./echo-test")

# Run on FPGA (default node)
run("echo-test", max_duration=1)

# Run on GPU with custom command
run("echo-test", node="GPU", max_duration=1,
    command="echo 123 > /data/gpu-downlink.txt")

# Schedule for future execution
scheduled_time = (datetime.now(tz) + timedelta(minutes=1)).isoformat()
run("echo-test", max_duration=1, scheduled_time=scheduled_time,
    command='sh -c "date > /data/time.txt"')
```

### 2. Pod Volumes (`example_pod_volumes`)

This example demonstrates the pod-name-to-volume storage model:

**What it does:**

- Creates a named pod (`pod-a`) which gets its own dedicated volume
- Runs a command that writes a file to the pod's volume
- Lists files specific to `pod-a`'s volume
- Uplinks files specifically to `pod-a`'s volume
- Shows that files in `pod-a` are not visible in the default volume
- Demonstrates that file operations must specify the correct `pod_name`
- Downlinks and deletes files from the specific pod volume

**Key concepts:**

- Pod-name-to-volume mapping
- Volume isolation between different pod names
- Importance of specifying `pod_name` for file operations
- Persistent storage across pod runs with the same name

**Code snippet:**

```python
# Create pod with dedicated volume
run("python:3.11-alpine", pod_name="pod-a", max_duration=30,
    command="echo 'Is this the final frontier?' > /data/hello-space.txt")

# Upload to pod-a's volume specifically
uplink(["hello-world.txt"], pod_name="pod-a")

# List pod-a's files
files_list(pod_name="pod-a")

# Default volume doesn't have pod-a's files
files_list()  # pod-a files not visible here

# Must specify pod_name for operations
delete("hello-world.txt", pod_name="pod-a")  # Works
delete("hello-world.txt")  # Fails - looks in default volume
```

### 3. Inter-Pod Communication (`example_pod_intercommunication`)

This example demonstrates how to make pods communicate within a private namespace:

**What it does:**

- Creates a private namespace for the user
- Starts a server pod that exposes port 80
- Starts a client pod that fetches data from the server
- Shows how pods reference each other using `<username>-<pod_name>:<port>`
- Downlinks the fetched data from the client pod's volume

**Key concepts:**

- Namespace creation for pod networking
- Port exposure with the `ports` parameter
- Inter-pod communication using pod naming convention
- Running multiple pods that interact with each other
- Network isolation per user namespace

**Code snippet:**

```python
# Create namespace first
namespace_create()

# Start server pod with exposed port
run("python:3.11-alpine", pod_name="server", max_duration=2,
    namespace=True, ports=[80],
    command="python -m http.server 80")

# Client pod fetches from server (client1-server:80)
run("python:3.11-alpine", pod_name="client", max_duration=1,
    namespace=True,
    command="wget client1-server:80/ -O /data/server-data.txt")

# Check what the client downloaded
files_list(pod_name="client")
downlink("server-data.txt", pod_name="client")
```

**Important:** Both pods must:

- Run with `namespace=True`
- Be created after namespace creation
- Use the naming convention `<username>-<pod_name>:<port>` for communication

### 4. Environmental Variables and arguments (`example_env_and_args`)

This example demonstrates how to use environment variables and arguments passed to the DPhi Pod.

**What it does:**

- Creates a pod with a command (a simple `/bin/sh -c` to spawn a terminal) that overrides the one by default in the Docker image.
- Sets environmental variables `DURATION` and `TIME` which will be used by our command.
- Sets arguments for the command, in which we `echo` the environment variables we set above.

**Code snippet:**

```python
run(
    "echo-test",
    max_duration=1,
    command="/bin/sh -c",
    args=["echo testing args $DURATION $SIZE", " > /data/test.txt"],
    envs={"DURATION": 60, "SIZE": 1024},
)
```

## Error Handling

The script includes an `examples_errors()` function that demonstrates common error scenarios:

- Attempting to downlink non-existent files
- Building with incorrect context paths
- Running non-existent Docker images
- Checking pod status when deployment fails

These examples help understand the error messages returned by the API.

## API Helper Functions

The script provides the following helper functions:

### Authentication

- `get_token()` - Authenticate and store JWT token
- `ensure_token()` - Automatically fetch token if needed

### File Operations

- `uplink(filepaths, dest_path="", pod_name="")` - Upload files
- `downlink(filepath, downlink_folder="downlink/", pod_name="")` - Download files
- `files_list(pod_name="")` - List files in volume
- `delete(filepath, pod_name="")` - Delete files or folders

### Docker Operations

- `image_build(dockerfile, image, context=".", pod_name="")` - Build Docker image
- `image_load(tarfile, image, pod_name="")` - Load image from tarball
- `image_list()` - List available images

### Pod Operations

- `run(image, node="FPGA", max_duration=1, command="", scheduled_time=None, pod_name=None, ports=None, namespace=False)` - Execute pod
- `pod_status(pod_name="")` - Check pod status
- `namespace_create()` - Create namespace for inter-pod communication

### HTTP Helpers

- `authorized_get(url, **kwargs)` - GET with auto-authentication
- `authorized_post(url, **kwargs)` - POST with auto-authentication

## Running the Examples

To run the examples:

```bash
# Run all examples
python em-api-interface.py

```

## Configuration

Default configuration in the script:

```python
BASE_URL = "http://localhost:8000/"
username = "client1"
password = ""
```

Modify these variables to match your environment and credentials.

## Best Practices

1. **Always check pod status** after scheduling - successful scheduling doesn't guarantee successful deployment
2. **Specify pod_name** when working with multiple volumes to avoid confusion
3. **Create namespace before** using port exposure features
4. **Use meaningful pod names** to keep track of different volumes
5. **Clean up resources** by deleting unused files
6. **Handle errors gracefully** - the API returns detailed error messages

## Next Steps

- Review the [API Specifications](/docs/4-em-api/02-api-specs.md) for detailed endpoint documentation
- Check the [Swagger documentation](https://editor.swagger.io/) with `em-api.json`
