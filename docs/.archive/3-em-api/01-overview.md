# Overview

The **Engineering Model (EM) API** provides a controlled environment to test software payloads and interact with CG2 in a manner analogous to operations in orbit. This API allows developers and engineers to perform uplinks, downlinks, and manage Docker-based payloads on a ground-based test system that simulates key aspects of the onboard environment.

## Purpose

Testing and validating satellite software can be challenging due to limited access to the spacecraft. To address this, we provide the EM API to:

- **Simulate Space operations on the ground:** Run commands and deploy software payloads as if interacting with CG2 in orbit.
- **Upload and manage files:** Uplink files to the onboard file system, retrieve them, and inspect content for debugging.
- **Execute Docker-based software payloads:** Build, load, and run software in a controlled environment, reflecting the deployment process on CG2.
- **Inspect and clean onboard directories:** List, download, and delete files safely, ensuring consistency with onboard file structures.

## Key Features

1. **Uplink Files**
   - Upload multiple files to the EM system.
   - Supports specifying destination directories and handling large payloads safely.
   - Files are packaged and transferred securely.

2. **Downlink Files**
   - Retrieve files from the simulated onboard filesystem.
   - Returns file content along with metadata (size, filename, hash).

3. **File Management**
   - List files with metadata including size and hash.
   - Delete files or directories remotely in a safe and controlled way.

4. **Docker Payload Management**
   - Build images using specified Dockerfiles and contexts, in an analogous air-gapped environment as in space..
   - Load prebuilt Docker images (tar files).
   - Run DPhi Pods simulating the execution environment onboard.
   - List available Docker images for validation and inspection.

## Why Use the EM API?

By interacting with the EM API, developers can:

- Validate software logic in a realistic environment before deploying to CG2.
- Test operational sequences such as file transfers and DPhi Pods execution.
- Detect issues early in the ground test environment rather than in orbit.
- Mimic end-to-end workflows of CG2 operations safely on Earth.

## Docker Images, Containers and DPhi Pods

### Docker Image

A Docker image is a packaged software environment that contains everything needed to run an application: the code, libraries, and dependencies.

Images are static — they do not change when executed.

You can build an image once and reuse it for multiple experiments.

The only requirement for EM API usage is that your Docker image must be built for arm64, matching the execution environment’s architecture.

### Docker Container

A container is a running instance of a Docker image.

Containers execute the commands defined in the image or commands provided at runtime.

They are ephemeral, meaning changes inside a container do not alter the original image unless explicitly saved.

Containers give you a controlled environment to run software consistently.

### DPhi Pod

A DPhi Pod is a wrapper around a container — technically, it is a Kubernetes pod that runs your container inside it, with extra features.

For simple experiments, running a container or a DPhi Pod produces the same result.

DPhi Pods allow more complex setups, such as scheduling, telemetry, and resource isolation.

They are named DPhi Pods to emphasize user-friendliness and the fact that they are adapted for the space environment simulation, making it easier to run software payloads on the EM.

### How It Works Together

The user provides a Docker image (or use one already available).

The EM API runs it inside a DPhi Pod, optionally with a command specified by the user.

If a command is not provided, the DPhi Pod runs the image’s default command.

If a command is provided, it overrides the default without needing to rebuild the image.

The user's dedicated volume is mounted at /data inside all DPhi Pod, allowing sharing of files and outputs across experiments.

## Example Workflow

1. **Authenticate:** Obtain a secure token to interact with the EM API.
2. **Uplink a Payload:** Upload Dockerfiles, scripts, or data files to the simulated onboard filesystem.
3. **Build and Load Images:** Prepare software payloads as Docker images, either by building the Docker image onboard or by loading a Docker image tarfile. Always keep in mind that building onboard is done in an air-gapped environment, which means that any command that needs internet connection (e.g. `pip install` or `apt-get update`) will fail the whole build.
4. **Execute a Pod:** Run the DPhi Pod to test the software payload.
5. **Downlink Results:** Retrieve logs, output files, or datasets for inspection.
6. **Cleanup:** Delete temporary files or images to maintain the system state.

---

This API acts as a **ground-based simulation of CG2 space operations**, enabling a safe, repeatable, and realistic test environment for CG2 software payloads. It bridges the gap between development and in-orbit deployment, providing confidence that the software will behave correctly when operating onboard.

---
