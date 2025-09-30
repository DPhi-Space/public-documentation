---
sidebar_position: 1
---

# Docker Best Practices in Space

This guide outlines best practices for building Docker containers optimized for use on **Clustergate-2**, considering the unique constraints of a space-based, air-gapped environment.

---

## Constraints

* Clustergate-2 is deployed in an **air-gapped environment**, meaning **no internet access** is available onboard. Only the **base Docker images** embedded **before launch** will be available.

* There is **no access to `apt`, `pip`, or other package managers** onboard. If your application requires additional dependencies, you’ll need to **manually include them** during the image build process (e.g., using direct `.apk` packages, pre-compiled `.pyc` files, or static binaries).

* **File transfer to and from the satellite is limited** and can be slow. You should **optimize your container images for size and efficiency** to ensure smooth deployment and data handling.

---

### Dockerfile Basics

Dockerfiles are declarative scripts that define how a container image is built. Key instructions include `FROM`, `COPY`, `RUN`, and more.

If you’re unfamiliar with Dockerfiles, start here:
[Dockerfile Syntax & Concepts](https://docs.docker.com/build/concepts/dockerfile/)

---

The Docker images can be built either on the ground locally, or in space by Clustergate-2. 

--- 

## In-Space Builds

For in-space builds, all required files—including the Dockerfile and any application binaries, scripts, or dependencies—must be uplinked to Clustergate-2. The system will then build the image onboard, based on the instructions in the Dockerfile.

The Dashboard allows you to upload and organize all files needed for your container build, while preserving the folder structure expected by your Dockerfile. When these files are selected for uplink to Clustergate-2, they will be transferred exactly as structured—maintaining the same directory layout.

Once onboard, the entire file set is placed in a private volume, which is then mounted into the container at runtime. This ensures your application has access to all the files it needs, in the locations your Dockerfile or entrypoint expects.

When building an image onboard, your Dockerfile must start with one of the base images already preloaded on the satellite using the `FROM` directive. These are the only Docker images available in space by default. Below is an example of Dockerfile that builds from a base image already onboard:

```bash
# Use one of the preloaded base images
FROM gcr.io/distroless/cc-debian12

# Copy the precompiled binary into the image
COPY my-app /my-app

# Set user permissions (optional but recommended for security)
USER 65532:65532

# Set the entry point
ENTRYPOINT ["/my-app"]
```

The folder structure would naturally be:

```bash
private-volume/
├── Dockerfile
└── my-app
```


Both the `Dockerfile` and the `my-app` binary must be uploaded to the Dashboard and selected for uplink to Clustergate-2. After the files are uplinked, you can request the Docker image to be built through the Dashboard by providing necessary details such as the image name, build context, and Dockerfile location. Once the build completes successfully, you will be able to run the container onboard.

---

## Ground Builds

Alternatively, if you need a custom base image, you can build it on the ground and upload it as a .tar archive using docker save. This method is suitable for lightweight images, as larger images may exceed uplink constraints. The next section explains how this works in more detail.

### Multi-Stage Builds

When the objective is to upload a new Docker image from scratch through a tar file, the recommended pattern is to use **multi-stage builds**. In this approach:

1. **Stage 1** builds your application, typically compiling it and linking it statically (so all dependencies are embedded).
2. **Stage 2** uses a **lightweight base image** (e.g., `alpine`, `distroless`) to package only the final binary for deployment.

This produces small, efficient containers that are easier to upload, load and run in orbit.

#### Example: Rust cross-compilation for ARM64
Check out the example in `examples/multi-stage-build`

```bash
FROM --platform=$BUILDPLATFORM tonistiigi/xx AS xx

FROM --platform=$BUILDPLATFORM rust:alpine AS builder
COPY --from=xx / /

RUN apk add clang lld musl-dev openssl-dev

ARG TARGETPLATFORM
WORKDIR /app
COPY src/ src/
COPY Cargo.toml .
COPY Cargo.lock .

RUN xx-cargo build --release --bin dphi-example --target-dir ./build && \
    xx-verify ./build/$(xx-cargo --print-target-triple)/release/dphi-example

RUN mv ./build/$(xx-cargo --print-target-triple)/release/dphi-example .

FROM gcr.io/distroless/cc-debian12
COPY --from=builder /app/dphi-example /dphi-example
USER 65532:65532
ENTRYPOINT ["/dphi-example"]
```

You would build this container **on the ground**, and then **export it to a `.tar` file** using:

```bash
docker buildx build --platform linux/arm64 -t dphi-example .
docker save dphi-example > dphi-example.tar
```

This `.tar` file can then be uploaded to the satellite, through the Dashboard. The system will load it to the Docker images on board by running: 

```bash
docker load < dphi-example.tar
```

---

### Binary Copy (Lightweight Approach)

In many cases, it’s even better to **pre-compile your binary with all dependencies embedded** (i.e., statically linked), then use a minimal Dockerfile to copy the binary into a lightweight base image.

For example, in Rust, statically linked binaries are the default. You can use a tool such as [`cross`](https://github.com/cross-rs/cross) to cross-compile for `arm64`:

```bash
cross build --target aarch64-unknown-linux-gnu --release
```

Then, use a simple Dockerfile:

```bash
FROM gcr.io/distroless/cc-debian12

COPY build/target/aarch64-unknown-linux-gnu/dphi-example /dphi-example

USER 65532:65532

ENTRYPOINT ["/dphi-example"]
```

To deploy this:

1. Package the **Dockerfile** and **compiled binary** together.
2. Build the image on the ground.
3. Export it as a `.tar` archive via `docker save`.
4. Upload the archive to the satellite through the Dashboard.

This approach is ideal for most applications—it produces **small, clean, and dependency-free containers**.

---

## Considerations

The main design goals for your Docker container in orbit are:

* **Minimize image size** to reduce upload time and storage use.
* **Embed all required dependencies** during the image build.
* **Avoid dynamic installation** of packages at runtime.
* **Use only base images that are already available on the satellite**.
* **Use static linking where possible** to simplify runtime requirements.

All files required for your container to function—**binary, input data, output data, and any necessary build files**—must be included in a **shared directory**. This ensures proper data exchange with the system, as there is no shell access inside the container during runtime.

## Adding a custom made Docker image pre-flight

Please cotact us ASAP for a chance to onboard a docker container before launch as the data throuput is limited in-orbit.
