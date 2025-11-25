import os

from datetime import datetime, timezone, timedelta
import base64
import json
import requests
import time
import datetime

BASE_URL = "http://localhost:8000/"
TOKEN = None

# Default credentials for testing
username = "client1"
password = "dphi_software!"


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


def files_list():
    """
    Retrieve a list of files on the users dedicated volume on CG2.
    """
    response = authorized_get(BASE_URL + "/em/files/list")
    return response.json()


def downlink(filepath, downlink_folder="downlink/"):
    """
    Downlink a file from the users dedicated volume and save it locally.

    Backend returns base64 content + metadata.

    filepath: filepath onboard to donwlink
    downlink_folder: local destination folder where to downlink the file
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


def delete(filepath):
    """
    Delete a file on the users dedicated folder on CG2.

    filepath: filepath to delete onboard. Can be a folder or a file.
    """
    response = authorized_post(
        BASE_URL + "em/files/delete",
        data={"filepath": filepath},
    )
    return response.json()


# ============================================================
# DOCKER / POD OPERATIONS
# ============================================================


def image_build(dockerfile, image, context="."):
    """
    Build a Docker image on CG2. The image is built on an air-gapped environment.

    dockerfile: Dockerfile path onboard to build the Docker image from
    image: Docker image name to tag the resulting build
    context: Docker build context from where to fetch the application source files
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/build",
        data={"dockerfile": dockerfile, "image": image, "context": context},
    )
    return response.json()


def image_load(tarfile, image):
    """
    Load a Docker image tarball on CG2.

    tarfile: File path from where to load the tar file of the Docker image.
    image: Docker image name from the tarfile. This parameter must match the Docker image name used during the build before creating the tar file.
    """
    response = authorized_post(
        BASE_URL + "em/pod/image/load",
        data={"tarfile": tarfile, "image": image},
    )
    return response.json()


def image_list():
    """
    List available Docker images on the EM for the user.
    """
    response = authorized_get(BASE_URL + "em/pod/image/list")
    return response.json()


def namespace_create():
    """
    Request a namespace creation for more complex operations where the user's DPhi Pods can communicate with each other onboard. This will create a namespace with the username as a prefix, and when DPhi Pod runs are requested to run with the namespace, they will be run in it.
    """
    response = authorized_post(
        BASE_URL + "em/pod/namespace/create",
    )
    return response.json()


def run(
    image,
    node="FPGA",
    max_duration=1,
    command="",
    scheduled_time=None,
    pod_name=None,
    ports=None,
    namespace=False,
):
    """
    Run a DPhi Pod on the EM with maximum execution time in minutes.

    image: Docker image to run
    node: node on which to run the DPhi Pod [FPGA,GPU,MPU]
    max_duration: maximum execution duration of the DPhi Pod in minutes before the system stops it gracefully.
    command(optional): linux bash command to run in the DPhi Pod. If none is provided, the default command embedded in the Docker image will be executed.
    scheduled_time(optional): schedule time when to run the DPhi Pod. If none is provided, it will be scheduled as soon as possible. The time must be provided in ISO format with timezone, e.g. 2025-05-22T12:10:00+02:00.
    pod_name(optional): sets the name of the DPhi Pod to run. DPhi Pod Names and dedicated volumes are linked. Meaning that running a pod with a different name will create a new dedicated volume with no data shared with previous pods runned with different names. When no name is provide, the default one is used and all the data is shared with the previous pods ran with the default name. Setting the name is especially useful when
    ports(optional): sets the ports to be exposed for this DPhi Pod. This allows the pod to expose a service to others pods running in the same namespace. Therefore, a namespace must be created before and the namespace parameter must be set to true for the ports to be taken into account.
    namespace(optional): sets the pod to be run inside a private namespace for the user, in which different pods can communicate between each other through the exposed ports. A namespace must be created beforehand.

    """
    response = authorized_post(
        BASE_URL + "em/pod/run",
        data={
            "image": image,
            "node": node,
            "max_duration": max_duration,
            "command": command,
            "scheduled_time": scheduled_time,
            "pod_name": pod_name,
            "ports": ports,
            "namespace": namespace,
        },
    )
    return response.json()


def pod_status():
    """
    Get current DPhi Pod execution status.
    """
    response = authorized_get(BASE_URL + "em/pod/status")
    return response.json()


# ============================================================
# MAIN — EXAMPLE WORKFLOW
# ============================================================

if __name__ == "__main__":
    # Try to authenticate
    if not get_token():
        exit(1)

    print("\n=== FILE LIST ===")
    print(json.dumps(files_list(), indent=4))

    print("\n=== UPLOAD FILES ===")
    print(
        uplink(
            [
                "./Dockerfile",
                "./echo-test.sh",
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
    time.sleep(10)

    print(
        run(
            "echo-test",
            node="GPU",
            max_duration=1,
            command="echo 123 > /data/gpu-downlink.txt",
        )
    )
    print(json.dumps(pod_status(), indent=4))

    time.sleep(10)

    # run container at a certain moment
    tz = timezone(timedelta(hours=2))
    scheduled_time = (datetime.datetime.now(tz) + timedelta(minutes=1)).isoformat()
    print(scheduled_time)
    command = 'sh -c "date > /data/time.txt"'
    print(
        run("echo-test", max_duration=1, scheduled_time=scheduled_time, command=command)
    )

    print("\n=== DOWNLINK FILE ===")
    downlink("downlink.txt")
    downlink("gpu-downlink.txt")
    downlink("time.txt")

    print("\n=== CLEANUP (DELETE FILES) ===")
    print(delete("/echo-test/Dockerfile"))
    print(delete("downlink.txt"))
    print(delete("time.txt"))
    print(delete("gpu-downlink.txt"))
    print(delete("/echo-test/echo-test.sh"))

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
            command="echo 123 > /data/gpu-downlink.txt",
        )
    )
    print(json.dumps(pod_status(), indent=4))
