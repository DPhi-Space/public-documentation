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


if __name__ == "__main__":
    print(
        uplink(
            [
                "Dockerfile",
                "fisheye.py",
                "resnet18-f37072fd.pth",
            ]
        )
    )
    print(image_build("Dockerfile", "fisheye-analysis", "."))
    print(run("fisheye-analysis", "GPU", 2))
    time.sleep(5)
    print(pod_status())
    print(json.dumps(files_list(), indent=4))

    print("Give it some time to analyse...")

    time.sleep(10)

    print(downlink("cuda_insights.json"))
    print(downlink("log.txt"))

    with open("downlink/cuda_insights.json", "r") as f:
        print(json.dumps(f.read(), indent=4))

    with open("downlink/log.txt", "r") as f:
        print(f.read())
