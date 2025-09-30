# Basics HowTo
This will aim to design best practices on how to build docker containers so that they are optimized to use on CG2.

## Constraints
- As we are on a air-gapped environment, keep in mind that there is only the base docker images embedded before launch that will be available.
- On board we don't have any apt nor pip cache repository, so everything you want to add to the base images will be dones by other ways (install direct apk, install direct py compiled code).
- The transfer of the files from/to the satellite is very limited and can take a lot of time, you will most likely need to optimize your application for size.

## Basics
### Dockerfile basics
Dockerfile have a quite simple struct with declarative keywords, such as  `FROM`, `COPY`, `RUN`,...
I would strongly advise you to take a look [here](https://docs.docker.com/build/concepts/dockerfile/) to have a base knowledge on where to get started.

The goal would then to build your application using the base images we provide (so as a `FROM` command).

### Dockerfile multi stage builds
Best would have a multi-stage build, one stage build the binary and link statically so that it embed eveything, then copy it over a lightweight image that we could upload as-is to the satellite.

Example in Rust to cross build for arm64 for example: 
```dockerfile
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

This example would then be built on Ground with a simple docker build command and then saved into a tar with the `docker save` command. Can be the case only for the lightweight images like alpine, distroless, and so on.

### Binary copy
Even better would be to compile binary with everything necessary embedded (look at statically linked library for example). Then have a Dockerfile that take one of the available image we have on board, copy the binary into it and run it as entrypoint if this use case is acceptable for you.
For example for Rust binaries this is the default, we can then use a tool like `cross` to cross compile to the desired architecture, arm64 in this case.
Then have a simple Dockerfile as example : 
```dockerfile=
FROM gcr.io/distroless/cc-debian12
COPY build/target/aarch64-unknown-linux-gnu/dphi-example /dphi-example
USER 65532:65532
ENTRYPOINT ["/dphi-example"]
```

Here we would need the Dockerfile and binary associated for upload to the satellite, this is most likely the way to go for most of the applications, as it will be lightweight.

## Considerations
The principal considerations to take into account to test your software in orbit would be the size of the upload artifacts, try to keep this in mind and have an application with the most of the dependencies embedded in your final image.https://hackmd.dphi.office/XQBQMODpS5aTAmaE8HDAeA?both#
