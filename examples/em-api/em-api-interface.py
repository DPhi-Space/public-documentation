"""
DPhi EM API Client Example
--------------------------

This script demonstrates how to interact programmatically with the CG2 EM API. It provides helper functions for authentication, file transfers, Docker image operations, and launching DPhi Pods on the EM. The goal is to offer a simple, local Python client that interacts with the provided EM API and makes it easy to automate workflows, manage pod runs, and inspect user-owned files inside the managed environment.

CG2 DPhi Pods Storage Model
----------------------

Each DPhi Pod name ("pod_name") corresponds to a unique persistent private
volume (PVC). The rules are:

- Using an existing pod_name -> reuses the same volume and its stored files.
- Using a new pod_name -> creates a new, empty, dedicated volume.
- Omitting pod_name -> uses the user's default pod and its default volume.
- All file operations (uplink, downlink, files_list, delete) and all pod runs
  use this same pod_name-to-volume mapping.

Files stored under one pod_name are NOT visible from another pod_name.

This is important when:
- Uploading files before running a pod
- Running multiple pods that should share or isolate data
- Accessing build contexts or configuration files inside different volumes
"""

import os
from datetime import datetime, timezone, timedelta
import base64
import json
import requests
import time
import datetime

BASE_URL = ""
TOKEN = None

username = ""
password = ""


# ============================================================
# AUTHENTICATION
# ============================================================


def get_token():
    """
    Authenticate to the backend and store the JWT access token.
    """
    global TOKEN, username, password

    response = requests.post(
        BASE_URL + "auth/",
        data={"username": username, "password": password},
    )
    content = response.json()

    if response.status_code == 200:
        TOKEN = content["access"]
        print("Access token acquired")
        return True

    print(f"Failed to get access token: {content.get('detail')}")
    return False


def ensure_token():
    """
    Ensures TOKEN exists. If not, fetch a new one.
    """
    if TOKEN is None:
        print("No token found. Fetching new token...")
        if not get_token():
            raise Exception("Authentication failed.")


# ============================================================
# AUTHORIZED REQUEST HELPERS
# ============================================================


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


# ============================================================
# FILE UPLOAD / DOWNLOAD OPERATIONS
# ============================================================


def uplink(filepaths, dest_path="", pod_name=""):
    """
    Upload files to the volume associated with `pod_name`.

    filepaths: list of local paths to upload
    dest_path (optional): remote destination folder
    pod_name (optional): selects which persistent volume the files are uploaded to. Uses the pod_name storage rules defined at the top of this file.
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
        data={"dest_path": dest_path, "pod_name": pod_name},
    )

    # Clean up file handles
    for _, (_, file_obj) in files_to_upload:
        file_obj.close()

    return response.json()


def files_list(pod_name=""):
    """
    List files stored in the volume associated with `pod_name`.

    pod_name (optional): selects which persistent volume to inspect. Uses the pod_name storage rules defined at the top of this file.
    """
    response = authorized_get(
        BASE_URL + "/em/files/list",
        params={"pod_name": pod_name} or {},
    )
    return response.json()


def downlink(filepath, downlink_folder="downlink/", pod_name=""):
    """
    Downlink a file from the volume associated with `pod_name`.

    filepath: filepath on the user's private volume to downlink.
    downlink_folder (optional): local folder where to downlink the files requested.
    pod_name (optional): selects which persistent volume to downlink from. Uses the pod_name storage rules defined at the top of this file.
    """

    ensure_token()
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Streaming GET request
    with requests.get(
        BASE_URL + "/em/files/downlink",
        headers=headers,
        params={"filepath": filepath, "pod_name": pod_name},
        stream=True,
    ) as response:
        if response.status_code != 200:
            # Parse JSON error and return it
            try:
                return response.json()
            except Exception:
                return {"error": "UNKNOWN_ERROR", "status": response.status_code}

        # Extract the filename from `Content-Disposition`
        cd = response.headers.get("Content-Disposition", "")
        filename = "downloaded_file"

        if "filename=" in cd:
            filename = cd.split("filename=", 1)[1].strip('"')

        # Prepare local folder
        os.makedirs(downlink_folder, exist_ok=True)
        local_path = os.path.join(downlink_folder, filename)

        # Write file to disk in chunks
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                if chunk:
                    f.write(chunk)

        print(f"File '{filename}' saved to {local_path}")
        return {
            "filename": filename,
            "local_path": local_path,
            "size_bytes": os.path.getsize(local_path),
        }


def delete(filepath, pod_name=""):
    """
    Delete a file or folder from the volume associated with `pod_name`.

    filepath: filepath on the user's private volume to delete onboard. Can be a folder or a file.
    pod_name (optional): selects which persistent volume to modify. Uses the pod_name storage rules defined at the top of this file.
    """
    response = authorized_post(
        BASE_URL + "em/files/delete",
        json={"filepath": filepath, "pod_name": pod_name},
    )
    return response.json()


# ============================================================
# DOCKER / POD OPERATIONS
# ============================================================


def image_build(dockerfile, image, context=".", pod_name=""):
    """
    build a docker image using files located in the user's volume. the dockerfile and build context must exist in the volume associated with `pod_name` (see storage model at top of file).


    dockerfile: dockerfile path onboard to build the docker image from
    image: docker image name to tag the resulting build
    context (optional): docker build context from where to fetch the application source files
    pod_name (optional): selects which persistent volume to use. uses the pod_name storage rules defined at the top of this file.
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/build",
        json={
            "dockerfile": dockerfile,
            "image": image,
            "context": context,
            "pod_name": pod_name,
        },
    )
    return response.json()


def image_load(tarfile, image, pod_name=""):
    """
    Load a Docker image tarball located in the user's volume. The tarfile must exist in the volume associated with `pod_name` (see storage model at top of file).


    tarfile: File path from where to load the tar file of the Docker image.
    image: Docker image name from the tarfile. This parameter must match the Docker image name used during the build before creating the tar file.
    pod_name (optional): selects which persistent volume to use. Uses the pod_name storage rules defined at the top of this file.
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/load",
        json={"tarfile": tarfile, "image": image, "pod_name": pod_name},
    )
    return response.json()


def image_list():
    """
    List available Docker images on the EM for the user.
    """
    response = authorized_get(BASE_URL + "em/pod/image/list")
    return response.json()


def run(
    image,
    node="FPGA",
    max_duration=1,
    command="",
    scheduled_time=None,
    pod_name=None,
    ports=None,
    args=None,
    envs=None,
):
    """
    Run a DPhi Pod on the EM with maximum execution time in minutes.

    image: Docker image to run
    node: node on which to run the DPhi Pod [FPGA,GPU,MPU]
    max_duration: maximum execution duration of the DPhi Pod in minutes before the system stops it gracefully.
    command(optional): linux bash command to run in the DPhi Pod. If none is provided, the default command embedded in the Docker image will be executed.
    scheduled_time(optional): schedule time when to run the DPhi Pod. If none is provided, it will be scheduled as soon as possible. The time must be provided in ISO format with timezone, e.g. 2025-05-22T12:10:00+02:00.
    pod_name (optional):
        Specifies which persistent volume the pod will use for its /data directory.
        Each pod_name maps to a dedicated volume:
        - Using an existing pod_name mounts its existing volume (files preserved).
        - Using a new pod_name creates a new, empty volume.
        - Omitting pod_name uses the user's default pod and its default volume.
        All file operations (uplink, downlink, files_list, delete) access the same
        volume selected here. See the storage model at the top of the file.
    ports(optional): sets the ports to be exposed for this DPhi Pod. This allows the pod to expose a service to others pods running owned by the user.
    envs(optional): sets environment variables inside the DPhi Pod. It must be passed as a dictionary with variable name and value mapping, e.g. {"DURATION": 60, "SIZE": 1024}.
    args(optional): sets the arguments to be passed to the command. It must be passed as a list of arguments, e.g. ['--debug', '-f', 'output.dat'].

    """
    response = authorized_post(
        BASE_URL + "em/pod/run",
        json={
            "image": image,
            "node": node,
            "max_duration": max_duration,
            "command": command,
            "scheduled_time": scheduled_time,
            "pod_name": pod_name,
            "ports": ports,
            "args": args,
            "envs": envs,
        },
    )
    return response.json()


def pod_status(pod_name=""):
    """
    Retrieve the status of the DPhi Pod associated with `pod_name`.

    pod_name (optional): Identifies which pod instance to query. Note that storage volumes also follow the pod_name rules defined at the top.
    """
    response = authorized_get(
        BASE_URL + "em/pod/status", params={"pod_name": pod_name} or {}
    )
    return response.json()


def example_pod_intercommunication():
    print("\n========== INTER-POD COMMUNICATION  ===========")
    print(
        "In this example we want to make to pods communicate over a given port. The client pod will fetch data from the server pod, therefore the server must expose a given port."
    )
    print(
        "\nThen we start the server pod. We must set the list of ports to expose to all the other user-owned pods running:"
    )
    print(
        run(
            "python:3.11-alpine",
            pod_name="server",
            max_duration=2,
            ports=[80],
            command="python -m http.server 80",
        )
    )

    print(
        "\nNow we run the client pod. It fetches data from the server pod, from the port it exposes i.e. 80, and saves it to its own private volume:"
    )
    print(
        run(
            "python:3.11-alpine",
            pod_name="client",
            max_duration=1,
            command="/usr/bin/wget",
            args=["server:80/", "-O", "/data/server-data.txt"],
        )
    )
    time.sleep(5)
    print("\nLets check the files it generated:")
    print(json.dumps(files_list(pod_name="client"), indent=4))
    time.sleep(5)

    print("\nAnd downlink it:")
    print(json.dumps(downlink("server-data.txt", pod_name="client"), indent=4))

    print("\nLets clean up the files:")
    print(json.dumps(delete("server-data.txt", pod_name="client"), indent=4))


def example_simple_operations():
    print("\n========== SIMPLE OPERATIONS ==========")
    print("\n=== FILE LIST ===")
    print(json.dumps(files_list(), indent=4))

    print("\n=== UPLOAD FILES ===")
    print(
        uplink(
            [
                "./simple-echo/Dockerfile",
                "./simple-echo/echo-test.sh",
            ],
            dest_path="echo-test",
        )
    )

    print("\n=== BUILD DOCKER IMAGE ===")
    print(
        image_build(
            "./echo-test/Dockerfile",
            "echo-test",
            "./echo-test",
        )
    )

    print("\n=== RUN DOCKER IMAGE ===")
    print(run("echo-test", max_duration=1))
    time.sleep(2)
    print(json.dumps(pod_status(), indent=4))
    time.sleep(30)

    print(
        run(
            "echo-test",
            node="GPU",
            max_duration=1,
            command="/bin/sh",
            args=[
                "-c",
                "echo 'if knowledge can create problems, it is not through ignorance that we can solve them' > /data/gpu-downlink.txt",
            ],
        )
    )
    time.sleep(5)

    print(json.dumps(pod_status(), indent=4))
    time.sleep(5)

    # run container at a certain moment
    tz = timezone(timedelta(hours=2))
    scheduled_time = (datetime.datetime.now(tz) + timedelta(minutes=1)).isoformat()
    command = 'sh -c "date > /data/time.txt"'
    print(
        run(
            "echo-test",
            max_duration=1,
            scheduled_time=scheduled_time,
            command="/bin/sh",
            args=[
                "-c",
                "echo 'if knowledge can create problems, it is not through ignorance that we can solve them' > /data/time.txt",
            ],
        )
    )

    print("\n=== DOWNLINK FILE ===")
    downlink("downlink.txt")
    downlink("orbital.json")
    downlink("gpu-downlink.txt")
    downlink("time.txt")

    print("\n=== CLEANUP (DELETE FILES) ===")
    print(delete("/echo-test/Dockerfile"))
    print(delete("orbital.json"))
    print(delete("downlink.txt"))
    print(delete("time.txt"))
    print(delete("gpu-downlink.txt"))
    print(delete("/echo-test"))


def example_pod_volumes():
    print("\n=== PODS WITH SPECIFIC NAMES ===")
    print(
        "Lets run a pod with a specified name, pod-a, which will create a new empty private volume for it:"
    )
    print(
        run(
            "python:3.11-alpine",
            pod_name="pod-a",
            max_duration=1,
            command="/bin/sh",
            args=["-c", "echo 'Is this the final frontier?' > /data/hello-space.txt"],
        )
    )
    print(
        "\nThen we will fetch the files from pod-a, which lives in a dedicated private persistent volume for it:"
    )
    print(json.dumps(files_list(pod_name="pod-a"), indent=4))
    print("\nThen we uplink a file for this specific pod:")
    print(
        uplink(
            [
                "./simple-echo/hello-world.txt",
            ],
            pod_name="pod-a",
        )
    )
    print("\nRechecking the files, we can see that it has been correctly uploaded:")
    print(json.dumps(files_list(pod_name="pod-a"), indent=4))

    print(
        "\nIf we check our default private volume, we can see it does not contain the hello-world.txt file:"
    )
    print(json.dumps(files_list(), indent=4))

    print(
        "\nIf we try to delete hello-world.txt without specifying the pod name, it will fail as it assumes the default private volume:"
    )
    print(json.dumps(delete("hello-world.txt"), indent=4))

    print("\nSo we specify pod-a for it to succeed:")
    print(json.dumps(delete("hello-world.txt", pod_name="pod-a"), indent=4))

    print("\nSame goes for downlinking files:")
    print(json.dumps(downlink("hello-space.txt", pod_name="pod-a"), indent=4))

    print("\nAnd we confirm by checking its files:")
    print(json.dumps(files_list(pod_name="pod-a"), indent=4))


def example_fisheye_api():
    print("\n=== FISHEYE API ===")
    print("Lets clean previous runs first.")
    print(delete("insight.json"))
    print(delete("20251029.png"))
    print(delete("20251031.png"))
    print(delete("20251030.png"))
    print(
        "\nIn this example we will test how to fetch images from the fisheye api, do some processing and downlink insighful data."
    )
    print("\nFirst we uplink the necessary files to build the Docker image:")
    print(uplink(["./fisheye-api/Dockerfile", "./fisheye-api/main.py"], "./fisheye"))

    print("\nThen we build the Docker Image:")
    print(image_build("fisheye/Dockerfile", "fisheye-analysis", "./fisheye"))

    print("\nWe request the pod to run:")
    print(run("fisheye-analysis", "FPGA", 30))

    print("\nWe verify the pod status:")
    time.sleep(5)
    print(pod_status())
    time.sleep(15)

    print("\nAfter it finished we will downlink the results and the image:")
    print(downlink("insights.json"))
    time.sleep(1)
    print(downlink("20251029.png"))


def examples_errors():
    print("\n\n=== Different Errors ===")
    print(json.dumps(downlink("inexistant-file.txt"), indent=4))
    print(
        json.dumps(
            image_build(
                "./echo-test/Dockerfile",
                "echo-test",
                "./echo2-test",
            ),
            indent=4,
        )
    )
    print(
        run(
            "echo12-test",
            node="GPU",
            max_duration=1,
        )
    )
    print(json.dumps(pod_status(), indent=4))
    print(
        run(
            "echo-test",
            node="GPU",
            max_duration=1,
            pod_name="Hey-there",
        )
    )
    print(json.dumps(pod_status(pod_name="Hey no whitespaces"), indent=4))


def example_args_and_envs():
    print(
        "\nWe can also set environment variables and arguments for the binary or command executed:"
    )
    print(
        run(
            "echo-test",
            max_duration=1,
            command="/bin/sh",
            args=["-c", "echo testing args $DURATION $SIZE > /data/argument-test.txt"],
            envs={"DURATION": 60, "SIZE": 1024},
        )
    )
    time.sleep(10)
    print(downlink("argument-test.txt"))
    print(
        "\nHere we can see that the environment variables have been used within the arguments passed to the echo command:\n"
    )
    with open("downlink/test.txt", "r") as f:
        print(f.read())
    print(delete("argument-test.txt"))


# ============================================================
# MAIN — EXAMPLE WORKFLOW
# ============================================================

if __name__ == "__main__":
    # Try to authenticate
    if not get_token():
        exit(1)

    example_pod_intercommunication()
    example_fisheye_api()
    example_args_and_envs()
    example_pod_volumes()
    example_simple_operations()
    examples_errors()
    exit(1)
